// SPDX-License-Identifier: MIT

pragma solidity ^0.8.2;

import "@openzeppelin/contracts/token/ERC1155/ERC1155.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/utils/math/SafeMath.sol";
import "@openzeppelin/contracts/utils/Counters.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";

import "./Coordinape.sol";

contract Coordinape1155 is ERC1155("some uri"), Ownable {
	using SafeMath for uint256;
	using Counters for Counters.Counter;
	using ECDSA for bytes32;


	uint256 public set;
	uint256 constant public DELIMITOR = 2 ** 255;
	IERC20 public grantToken;
	address public treasury;

	mapping(uint256 => uint256) public grants;
	mapping(uint256 => uint256) public giveSupply;

	mapping(address => bool) public recurrent;
	mapping(address => bool) public whitelist;
	mapping(uint256 => bool) public grantCheck;

	mapping(uint256 => Counters.Counter) private _participantsIds;
	mapping(uint256 => mapping(address => uint8)) private _participants;
	mapping(uint256 => mapping(uint256 => address)) private _participantsAddresses;
	mapping(uint256 => mapping(address => uint256)) private _unspent;
	mapping(uint256 => mapping(address => bool)) private _hasAllocated;

	mapping(uint256 => uint256) private _amounts;

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
		_amounts[_epoch] = _amount;
		grants[_epoch] = _grant;
	}

	function addParticipant(uint256 _epoch, address _recipient, uint8 _perms) external onlyOwner {
        require(
            _perms & Coordinape.PARTICIPANT != 0,
            "permissions must contain at least 'PARTICIPANT'."
        );
        require(
            _participants[_epoch][_recipient] == Coordinape.EXTERNAL,
            "recipient is already a participant."
        );
        _participantsAddresses[_epoch][_participantsIds[_epoch].current()] = _recipient;
        _participants[_epoch][_recipient] = _perms;
		// do we need?
        //_unspent[epoch][recipient] = _amount;
		
		//_mint(_recipient, _epoch, _amount[_epoch], "");
        Counters.increment(_participantsIds[_epoch]);
    }

	function removeParticipant(uint256 _epoch, address _recipient) external onlyOwner {
        require(
            _participants[_epoch][_recipient] & Coordinape.RECEIVER != 0,
            "sender is already a non-receiver participant."
        );
        _participants[_epoch][_recipient] = Coordinape.PARTICIPANT;
        //_burn(recipient, _epoch, balanceOf(recipient));
    }

	function participants(uint256 _epoch) public view returns (address[] memory) {
        address[] memory addresses = new address[](Counters.current(_participantsIds[_epoch]));
        for (uint256 i = 0; i < Counters.current(_participantsIds[_epoch]); i++) {
            addresses[i] = _participantsAddresses[_epoch][i];
        }
        return addresses;
    }


	// research merkle proof path could also be a nice approach, open for discussion
	function sync(
		uint256 _epoch,
		address _giver,
		address[] calldata _receivers,
		uint256[] calldata _alloc,
		bytes calldata _sig)
		external onlyOwner {
		require(_hasAllocated[_epoch][_giver], "Giver already allocated");
		require(_alloc.length == _receivers.length, "array length not equal");
		require(keccak256(abi.encodePacked(_receivers, _alloc)).recover(_sig) == _giver,
			"Invalid signature");
		require(isSubAmount(_alloc), "Allocations are above 100");
		checkReceivers(_epoch, _receivers);
		for(uint256 i = 0; i < _receivers.length; i++)
			_mint(_receivers[i], _epoch + DELIMITOR, _alloc[i], "");
		_hasAllocated[_epoch][_giver] = true;
	}

	function isSubAmount(uint256[] calldata _alloc) internal pure returns (bool) {
		uint256 sum;
		for (uint256 i = 0 ; i < _alloc.length; i++)
			sum += _alloc[i];
		return sum <= 100;
	}
	
	function checkReceivers(uint256 _epoch, address[] calldata _receivers) internal view {
		for (uint256 i = 0 ; i < _receivers.length; i++) {
			uint8 perms = _participants[_epoch][_receivers[i]];
			require(perms & Coordinape.PARTICIPANT != 0
				&& perms & Coordinape.RECEIVER != 0,
				"Receiver not participatnig or has opted out.");
		}

	}

	// /*
	//  * Create a new grant round. Will revert if previous round hasn't been funded yet
	//  * 
	//  * _amount: Amount of $GIVE to mint
	//  */
	// function mintNewSet(uint256 _amount) external onlyOwner {
	// 	require(grantCheck[set], "Coordinapes: previous grant not supplied");
	// 	set++;
	// 	_mint(msg.sender, set, _amount, "");
	// }

	// /*
	//  * Fund current month allocation from either treasury (if set) or sender
	//  * 
	//  * _amount: Amount of yUSD to distribute on current grant roune
	//  */
	// function supplyGrants(uint256 _amount) external onlyOwner {
	// 	if (treasury != address(0))
	// 		yUSD.transferFrom(treasury, address(this), _amount);
	// 	else
	// 		yUSD.transferFrom(msg.sender, address(this), _amount);
	// 	funds[set] = funds[set].add(_amount);
	// 	grantCheck[set] = true;
	// }

	// /*
	//  * Sends $GIVE tokens on a whitelisted member which get converted to $GET tokens
	//  * 
	//  *     _to: Receiver of $GET
	//  * _amount: Amount of $GIVE to burn and $GET to mint
	//  */
	// function give(address _to, uint256 _amount) external {
	// 	require(_to != msg.sender, "Coordinape: sender cannot be receiver");
	// 	require(whitelist[msg.sender], "Coordinape: sender not whitelisted");
	// 	require(whitelist[_to], "Coordinape: receiver not whitelisted");
	// 	require(!recurrent[_to], "Coordinape: receiver cannot be recurrent");

	// 	_burn(msg.sender, set, _amount);
	// 	_mint(_to, set.add(DELIMITOR), _amount, "");
	// 	giveSupply[set.add(DELIMITOR)] = giveSupply[set.add(DELIMITOR)].add(_amount);
	// }

	// /*
	//  * Burn $GET tokens to receive yUSD at the end of each grant rounds
	//  * 
	//  *     _set: Set from which to collect funds
	//  * _amount: Amount of $GET to burn to receive yUSD
	//  */
	// function get(uint256 _set, uint256 _amount) external {
	// 	require(whitelist[msg.sender], "Coordinape: sender not whitelisted");
	// 	uint256 _funds = funds[_set];
	// 	require(_funds > 0, "Coordinapes: No funds");
	// 	uint256 supply = giveSupply[_set.add(DELIMITOR)];
	// 	uint256 grant = _funds.mul(_amount).div(supply);

	// 	_burn(msg.sender, _set + DELIMITOR, _amount);
	// 	funds[_set] = funds[_set].sub(grant);
	// 	giveSupply[_set.add(DELIMITOR)] = supply.sub(_amount);
	// 	grantToken.transfer(msg.sender, grant);
	// }

	// modifier authorised() {
	// 	require(authorised[msg.sender], "not authorised");
	// 	 _;
	// }
}