pragma solidity ^0.8.2;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/cryptography/MerkleProof.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol"; 
import "./wrapper/ApeVault.sol";
import "./ApeAllowanceModule.sol";

contract ApeDistributor is ApeAllowanceModule, Ownable {
	using MerkleProof for bytes32[];
	using SafeERC20 for IERC20;

	uint256 public tierCFee = 250;
	// uint256 tierBFee = 250;
	// uint256 tierAFee = 250;


	// address to approve admins for a circle
	mapping(address => address) public approvals;

	// vault => circle => bool
	mapping(address => mapping(address => bool)) public circlesOfVault;

	// accepted tokens for given circle
	// circle => grant token => bool
	mapping(address => mapping(address => bool)) public circleToken;

	// roots following this mapping:
	// circle address => token address => epoch ID => root
	mapping(address =>mapping(address => mapping(uint256 => bytes32))) public epochRoots;
	mapping(address =>mapping(address => uint256)) public epochTracking;
	mapping(address => mapping(address => mapping(uint256 => mapping(uint256 => uint256)))) public epochClaimBitMap;

	// checkpoints following this mapping:
	// circle => token => address => checkpoint
	mapping(address => mapping(address => mapping(address => uint256))) public checkpoints;

	event Claimed(address circle, address token, uint256 epoch, uint256 index, address account, uint256 amount);

	event apeVaultFundsTapped(address indexed apeVault, address yearnVault, uint256 amount);

	function updateCFee(uint256 _newFee) external onlyOwner {
		tierCFee = _newFee;
	}

	function uploadEpochRoot(
		address _vault,
		address _circle,
		address _token,
		bytes32 _root,
		uint256 _amount,
		uint256 _slippage,
		uint8 _tapType)
		external {
		require(circlesOfVault[_vault][_circle], "Vault cannot serve circle");
		require(approvals[_circle] == msg.sender, "Sender cannot upload a root");
		require(circleToken[_circle][_token], "Token not accepted");
		_isTapAllowed(_vault, _circle, _token, _amount);
		uint256 epoch = epochTracking[_circle][_token];
		epochRoots[_circle][_token][epoch] = _root;

		epochTracking[_circle][_token]++;

		uint256 sharesRemoved = ApeVaultWrapper(_vault).tap(_amount, _slippage, _tapType);
		if (sharesRemoved > 0)
			emit apeVaultFundsTapped(_vault, address(ApeVaultWrapper(_vault).vault()), sharesRemoved);
	}

	function updateCircleToVault(address _circle, bool _value) external {
		circlesOfVault[msg.sender][_circle] = _value;
	}

	function updateCircleAdmin(address _circle, address _admin) external {
		require(circlesOfVault[msg.sender][_circle], "Circle not attached to vault");
		approvals[_circle] = _admin;
	}

	function updateTokensOfCircle(address _circle, address _token, bool _val) external {
		require(approvals[_circle] == msg.sender, "Sender cannot update tokens");
		circleToken[_circle][_token] = _val;
	}

	function isClaimed(address _circle, address _token, uint256 _epoch, uint256 _index) public view returns(bool) {
		uint256 wordIndex = _index / 256;
		uint256 bitIndex = _index % 256;
		uint256 word = epochClaimBitMap[_circle][_token][_epoch][wordIndex];
		uint256 bitMask = 1 << bitIndex;
		return word & bitMask == bitMask;
	}

	function _setClaimed(address _circle, address _token, uint256 _epoch, uint256 _index) internal {
		uint256 wordIndex = _index / 256;
		uint256 bitIndex = _index % 256;
		epochClaimBitMap[_circle][_token][_epoch][wordIndex] |= 1 << bitIndex;
	}

	function claim(address _circle, address _token, uint256 _epoch, uint256 _index, address _account, uint256 _checkpoint, bytes32[] memory _proof) external {
		require(!isClaimed(_circle, _token, _epoch, _index), "Claimed already");
		bytes32 node = keccak256(abi.encodePacked(_index, _account, _checkpoint));
		require(_proof.verify(epochRoots[_circle][_token][_epoch], node), "Wrong proof");
		uint256 currentCheckpoint = checkpoints[_circle][_token][_account];
		require(_checkpoint > currentCheckpoint, "Given checkpoint not higher than current checkpoint");
		
		uint256 claimable = _checkpoint - currentCheckpoint;
		checkpoints[_circle][_token][_account] = _checkpoint;
		_setClaimed(_circle, _token, _epoch, _index);
		IERC20(_token).safeTransfer(_account, claimable);
		emit Claimed(_circle, _token, _epoch, _index, _account, claimable);
	}
}