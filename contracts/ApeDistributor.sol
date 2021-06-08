pragma solidity ^0.8.2;

import "@openzeppelin/contracts/utils/cryptography/MerkleProof.sol";

contract ApeDistributor {
	using MerkleProof for bytes32[];

	mapping(address => address) public approvals;
	mapping(address => address) public circleToken;

	mapping(address => mapping(uint256 => bytes32)) public epochRoots;
	mapping(address => mapping(uint256 => mapping(uint256 => uint256))) public epochClaimBitMap;

	event Claimed(address circle, uint256 epoch, uint256 index, address account, uint256 amount);

	function isClaimed(address _circle, uint256 _epoch, uint256 _index) public view returns(bool) {
		uint256 wordIndex = _index / 256;
		uint256 bitIndex = _index % 256;
		uint256 word = epochClaimBitMap[_circle][_epoch][wordIndex];
		uint256 bitMask = 1 << bitIndex;
		return word & bitMask == bitMask;
	}

	function _setClaimed(address _circle, uint256 _epoch, uint256 _index) internal {
		uint256 wordIndex = _index / 256;
		uint256 bitIndex = _index % 256;
		epochClaimBitMap[_circle][_epoch][wordIndex] |= 1 << bitIndex;
	}

	function claim(uint256 _circle, uint256 _epoch, uint256 _index, address _account, uint256 _amount, bytes32[] memory _proof) external {
		require(!isClaimed(_circle, _epoch, _index), "Claimed already");
		bytes32 node = keccak256(abi.encodePacked(_index, _account, _amount));
		require(_proof.verify(epochRoots[_epoch], node), "Wrong proof");
		
		_setClaimed(_circle, _epoch, _index);
		//transfer
		emit Claimed(_epoch, _index, _account, _amount);
	}
}