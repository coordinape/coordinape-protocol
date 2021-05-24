// SPDX-License-Identifier: MIT

pragma solidity ^0.8.2;

import "@openzeppelin/contracts/token/ERC1155/ERC1155.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/utils/math/SafeMath.sol";
import "@openzeppelin/contracts/utils/Counters.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
import "@openzeppelin/contracts/utils/cryptography/MerkleProof.sol";

import "./Coordinape.sol";
import "./CoordinapeCircle.sol";
import "./MerkleDistributor.sol";

contract TokenSet is ERC1155("some uri"), Ownable, MerkleDistributor {
	using SafeMath for uint256;
	using Counters for Counters.Counter;
	using MerkleProof for bytes32[];


	uint256 public set;
	uint256 constant public DELIMITOR = 2 ** 255;
	IERC20 public grantToken;
	address public treasury;

	mapping(uint256 => uint256) public grants;
	mapping(uint256 => uint256) public grantAmounts;
	mapping(uint256 => uint256) public getSupply;
	mapping(uint256 => Counters.Counter) private _participantsIds;
	mapping(uint256 => mapping(address => uint8)) private _participantsPerms;
	mapping(uint256 => mapping(uint256 => address)) private _participantsAddresses;
	//mapping(uint256 => mapping(address => uint256)) private _unspent;
	mapping(uint256 => mapping(address => bool)) private _hasAllocated;

	mapping(uint256 => uint256) private _maxAlocation;

	mapping(address =>  bool) public authorised;

	constructor(address _grant) {
		grantToken = IERC20(_grant);
	}

	function setCaller(address _caller, bool _val) external onlyOwner {
		authorised[_caller] = _val;
	}

	function setTreasury(address _treasury) external onlyOwner {
		treasury = _treasury;
	}

	function startEpoch(uint256 _epoch, uint256 _amount, uint256 _grant) external onlyOwner {
		_maxAlocation[_epoch] = _amount;
		grants[_epoch] = _grant;
	}

	function addParticipant(uint256 _epoch, address _recipient, uint8 _perms) external onlyOwner {
        require(
            _perms & Coordinape.PARTICIPANT != 0,
            "permissions must contain at least 'PARTICIPANT'."
        );
        require(
            _participantsPerms[_epoch][_recipient] == Coordinape.EXTERNAL,
            "recipient is already a participant."
        );
        _participantsAddresses[_epoch][_participantsIds[_epoch].current()] = _recipient;
        _participantsPerms[_epoch][_recipient] = _perms;
		// do we need?
        //_unspent[epoch][recipient] = _amount;
		
		//_mint(_recipient, _epoch, _amount[_epoch], "");
        Counters.increment(_participantsIds[_epoch]);
    }

	function removeParticipant(uint256 _epoch, address _recipient) external onlyOwner {
        require(
            _participantsPerms[_epoch][_recipient] & Coordinape.RECEIVER != 0,
            "sender is already a non-receiver participant."
        );
        _participantsPerms[_epoch][_recipient] = Coordinape.PARTICIPANT;
        //_burn(recipient, _epoch, balanceOf(recipient));
    }

	function participants(uint256 _epoch) public view returns (address[] memory) {
        address[] memory addresses = new address[](Counters.current(_participantsIds[_epoch]));
        for (uint256 i = 0; i < Counters.current(_participantsIds[_epoch]); i++) {
            addresses[i] = _participantsAddresses[_epoch][i];
        }
        return addresses;
    }

	function lockEpochMerkleRoot(uint256 _epoch, bytes32 _merkleRoot, uint256 _epochGetSupply) external onlyOwner {
		require(CoordinapeCircle(owner()).state(_epoch) == 0, "Wrong state to sync");
		require(_epochGetSupply > 0, "Get supply cannot be 0");
		epochRoots[_epoch] = _merkleRoot;
		getSupply[_epoch] = _epochGetSupply;
	}

	


	/*
	 * Fund current month allocation from either treasury (if set) or sender
	 * 
	 * _amount: Amount of yUSD to distribute on current grant roune
	 */
	function supplyGrant(uint256 _epoch) external onlyOwner {
		if (treasury != address(0))
			grantToken.transferFrom(treasury, address(this), grants[_epoch]);
		else
			grantToken.transferFrom(msg.sender, address(this), grants[_epoch]);
		grantAmounts[_epoch] = grants[_epoch];
	}

	function claim(uint256 _epoch, uint256 _index, address _account, uint256 _amount, bytes32[] memory _proof) external override {
		require(!isClaimed(_epoch, _index), "Claimed already");
		bytes32 node = keccak256(abi.encodePacked(_index, _account, _amount));
		require(_proof.verify(epochRoots[_epoch], node), "Wrong proof");
		
		_setClaimed(_epoch, _index);
		_mint(_account, _epoch + DELIMITOR, _amount, "");
		emit Claimed(_epoch, _index, _account, _amount);
	}

	/*
	 * Burn $GET tokens to receive yUSD at the end of each grant rounds
	 * 
	 *     _set: Set from which to collect funds
	 * _amount: Amount of $GET to burn to receive yUSD
	 */
	function get(uint256 _epoch) external {
		require(CoordinapeCircle(owner()).state(_epoch) == 2, "Wrong state to get");
		uint256 balance = balanceOf(msg.sender, _epoch + DELIMITOR);
		require(balance > 0, "No Get tokens");
		uint256 grant = grantAmounts[_epoch];
		require(grant > 0, "No funds");
		uint256 supply = getSupply[_epoch.add(DELIMITOR)];
		uint256 alloc = grant.mul(balance).div(supply);

		_burn(msg.sender, _epoch + DELIMITOR, balance);
		grantAmounts[_epoch] -= alloc;
		getSupply[_epoch.add(DELIMITOR)] -= balance;
		grantToken.transfer(msg.sender, alloc);
	}


	function burnGet(uint256 _epoch, address _getter, uint256 _amount) external {
		require(CoordinapeCircle(owner()).state(_epoch) == 1, "Wrong state to burn");
		uint256 balance = balanceOf(msg.sender, _epoch + DELIMITOR);
		require(_amount <= balance, "burn amount too large");

		if (_getter == address(0)) {
			getSupply[_epoch.add(DELIMITOR)] -= balance;
			_burn(msg.sender, _epoch + DELIMITOR, _amount);
		}
		else {
			uint8 perms = _participantsPerms[_epoch][_getter];
			require(perms & Coordinape.PARTICIPANT != 0
				&& perms & Coordinape.RECEIVER != 0,
				"Receiver not participatnig or has opted out.");
			TokenSet.safeTransferFrom(msg.sender, _getter, _epoch + DELIMITOR, _amount, "");
		}
	}

	function permissionsOf(uint256 _epoch, address _recipient) public view returns (uint8) {
        return _participantsPerms[_epoch][_recipient];
    }

    function isParticipant(uint256 _epoch, address _recipient) public view returns (bool) {
        return _participantsPerms[_epoch][_recipient] & Coordinape.PARTICIPANT != 0;
    }

	// we could have this again as the only token minted would be grant-backed
	function safeTransferFrom(
        address from,
        address to,
        uint256 id,
        uint256 amount,
        bytes memory data
    )
        public
        virtual
        override
		onlyOwner
    {
		super.safeTransferFrom(from, to, id, amount, data);
	}


	function safeBatchTransferFrom(
        address from,
        address to,
        uint256[] memory ids,
        uint256[] memory amounts,
        bytes memory data
    )
        public
        virtual
        override
    {
		revert();
	}
	// modifier authorised() {
	// 	require(authorised[msg.sender], "not authorised");
	// 	 _;
	// }
}