// SPDX-License-Identifier: MIT

pragma solidity ^0.8.2;

import "@openzeppelin/contracts/utils/cryptography/MerkleProof.sol";

abstract contract MerkleDistributor {
	using MerkleProof for bytes32[];

	mapping(uint256 => bytes32) public epochRoots;
	mapping(uint256 => mapping(uint256 => uint256)) public epochClaimBitMap;

	event Claimed(uint256 epoch, uint256 index, address account, uint256 amount);

	function isClaimed(uint256 _epoch, uint256 _index) public view returns(bool) {
		uint256 wordIndex = _index / 256;
		uint256 bitIndex = _index % 256;
		uint256 word = epochClaimBitMap[_epoch][wordIndex];
		uint256 bitMask = 1 << bitIndex;
		return word & bitMask == bitMask;
	}

	function _setClaimed(uint256 _epoch, uint256 _index) internal {
		uint256 wordIndex = _index / 256;
		uint256 bitIndex = _index % 256;
		epochClaimBitMap[_epoch][wordIndex] |= 1 << bitIndex;
	}

	function claim(uint256 _epoch, uint256 _index, address _account, uint256 _amount, bytes32[] memory _proof) external virtual;
}