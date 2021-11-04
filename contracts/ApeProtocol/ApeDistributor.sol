pragma solidity ^0.8.2;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/cryptography/MerkleProof.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol"; 
import "./wrapper/ApeVault.sol";
import "./ApeAllowanceModule.sol";
import {VaultAPI} from "./wrapper/BaseWrapper.sol";

contract ApeDistributor is ApeAllowanceModule, Ownable {
	using MerkleProof for bytes32[];
	using SafeERC20 for IERC20;


	// address to approve admins for a circle
	// vault => circle => admin address
	mapping(address => mapping(bytes32 => address)) public vaultApprovals;

	// accepted tokens for given circle
	// circle => grant token => bool
	// mapping(address => mapping(address => bool)) public circleToken;

	// roots following this mapping:
	// circle address => token address => epoch ID => root
	mapping(bytes32 =>mapping(address => mapping(uint256 => bytes32))) public epochRoots;
	mapping(bytes32 =>mapping(address => uint256)) public epochTracking;
	mapping(bytes32 => mapping(address => mapping(uint256 => mapping(uint256 => uint256)))) public epochClaimBitMap;

	mapping(bytes32 => mapping(address => uint256)) public circleAlloc;

	// checkpoints following this mapping:
	// circle => token => address => checkpoint
	mapping(bytes32 => mapping(address => mapping(address => uint256))) public checkpoints;

	event AdminApproved(address indexed vault, bytes32 indexed circle, address indexed admin);

	event Claimed(bytes32 circle, address token, uint256 epoch, uint256 index, address account, uint256 amount);

	event apeVaultFundsTapped(address indexed apeVault, address yearnVault, uint256 amount);

	function uploadEpochRoot(
		address _vault,
		bytes32 _circle,
		address _token,
		bytes32 _root,
		uint256 _amount,
		uint8 _tapType)
		external {
		require(vaultApprovals[_vault][_circle] == msg.sender || ApeVaultWrapper(_vault).owner() == msg.sender, "Sender cannot upload a root");
		require(address(ApeVaultWrapper(_vault).vault()) == _token, "Vault cannot supply token");
		// require(circleToken[_circle][_token], "Token not accepted");
		_isTapAllowed(_vault, _circle, _token, _amount);
		uint256 epoch = epochTracking[_circle][_token];
		epochRoots[_circle][_token][epoch] = _root;

		epochTracking[_circle][_token]++;
		circleAlloc[_circle][_token] += _amount;
		uint256 beforeBal = IERC20(_token).balanceOf(address(this));
		uint256 sharesRemoved = ApeVaultWrapper(_vault).tap(_amount, _tapType);
		uint256 afterBal = IERC20(_token).balanceOf(address(this));
		require(afterBal - beforeBal == _amount, "Did not receive correct amount of tokens");
		if (sharesRemoved > 0)
			emit apeVaultFundsTapped(_vault, address(ApeVaultWrapper(_vault).vault()), sharesRemoved);
	}

	function updateCircleAdmin(bytes32 _circle, address _admin) external {
		vaultApprovals[msg.sender][_circle] = _admin;
		emit AdminApproved(msg.sender, _circle, _admin);
	}

	function isClaimed(bytes32 _circle, address _token, uint256 _epoch, uint256 _index) public view returns(bool) {
		uint256 wordIndex = _index / 256;
		uint256 bitIndex = _index % 256;
		uint256 word = epochClaimBitMap[_circle][_token][_epoch][wordIndex];
		uint256 bitMask = 1 << bitIndex;
		return word & bitMask == bitMask;
	}

	function _setClaimed(bytes32 _circle, address _token, uint256 _epoch, uint256 _index) internal {
		uint256 wordIndex = _index / 256;
		uint256 bitIndex = _index % 256;
		epochClaimBitMap[_circle][_token][_epoch][wordIndex] |= 1 << bitIndex;
	}

	function claim(bytes32 _circle, address _token, uint256 _epoch, uint256 _index, address _account, uint256 _checkpoint, bool _redeemShares, bytes32[] memory _proof) public {
		require(!isClaimed(_circle, _token, _epoch, _index), "Claimed already");
		bytes32 node = keccak256(abi.encodePacked(_index, _account, _checkpoint));
		require(_proof.verify(epochRoots[_circle][_token][_epoch], node), "Wrong proof");
		uint256 currentCheckpoint = checkpoints[_circle][_token][_account];
		require(_checkpoint > currentCheckpoint, "Given checkpoint not higher than current checkpoint");
		
		uint256 claimable = _checkpoint - currentCheckpoint;
		require(claimable <= circleAlloc[_circle][_token], "Can't claim more than circle has to give");
		circleAlloc[_circle][_token] -= claimable;
		checkpoints[_circle][_token][_account] = _checkpoint;
		_setClaimed(_circle, _token, _epoch, _index);
		if (_redeemShares && msg.sender == _account)
			VaultAPI(_token).withdraw(claimable, _account);
		else
			IERC20(_token).safeTransfer(_account, claimable);
		emit Claimed(_circle, _token, _epoch, _index, _account, claimable);
	}

	function claimMany(
		bytes32[] calldata _circles,
		address[] calldata _tokensAndAccounts,
		uint256[] calldata _epochsIndexesCheckpoints,
		bool[] calldata _redeemShares,
		bytes32[][] memory _proofs) external {
		for(uint256 i = 0; i < _circles.length; i++) {
			claim(
				_circles[i],
				_tokensAndAccounts[i],
				_epochsIndexesCheckpoints[i],
				_epochsIndexesCheckpoints[i + _epochsIndexesCheckpoints.length / 3],
				_tokensAndAccounts[i + _tokensAndAccounts.length / 2],
				_epochsIndexesCheckpoints[i + _epochsIndexesCheckpoints.length * 2 / 3],
				_redeemShares[i],
				_proofs[i]
				);
		}
	}
}	