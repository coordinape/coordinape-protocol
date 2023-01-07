// SPDX-License-Identifier: AGPL-3.0-only
pragma solidity ^0.8.2;

import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract CoSoul is ERC721("CoSoul", "Soul"), Ownable {
	using ECDSA for bytes32;

	bool public initiated;
	address public signer;
	mapping(address => bool) public authorisedCallers;
	mapping(uint256 => uint256) public transferNonces;
	mapping(uint256 => uint256) public syncNonces;
	mapping(uint256 => uint256) public burnNonces;
	mapping(address => uint256) public mintNonces;
	uint256 public counter;
	mapping(uint256 => uint256) public blobs;
	

	modifier authorised(address _operator) {
		require(authorisedCallers[_operator] || _operator == owner());
		_;
	}

	function init(string memory __name, string memory __symbol, address _signer) external {
		require(!initiated);
		initiated = true;
		_name = __name;
		_symbol = __symbol;
		_owner = msg.sender;
		signer = _signer;
	}

	function setSigner(address _signer) external onlyOwner {
		signer = _signer;
	}


	function setCallers(address _caller, bool _val) external onlyOwner {
		authorisedCallers[_caller] = _val;
	}

	function getSlot(uint8 _slot, uint256 _tokenId) public view returns(uint256 value) {
		require(_slot < 8);

		uint256 current = blobs[_tokenId];
		uint256 mask = 0xffffffff << _slot;
		value = (current & mask) >> _slot;
	}

	function setSlot(uint256 _slot, uint32 _amount, uint256 _tokenId) external authorised(msg.sender) {
		require(_slot < 8);

		uint256 current = blobs[_tokenId];
		uint256 mask = ~(0xffffffff << _slot);
		blobs[_tokenId] = (current & mask) | (_amount << _slot);
	}

	function incSlot(uint8 _slot, uint256 _amount, uint256 _tokenId) external authorised(msg.sender) {
		require(_slot < 8);
		uint256 value = getSlot(_slot, _tokenId);
		require(value + _amount <= type(uint32).max, "CoSoul: uint32 overflow");
		uint256 current = blobs[_tokenId];
		blobs[_tokenId] = current + (_amount << _slot);
	}

	function decSlot(uint8 _slot, uint256 _amount, uint256 _tokenId) external authorised(msg.sender) {
		require(_slot < 8);
		uint256 value = getSlot(_slot, _tokenId);
		require(value >= _amount, "CoSoul: uint32 overflow");
		uint256 current = blobs[_tokenId];
		blobs[_tokenId] = current - (_amount << _slot);
	}

	function syncWithSignature(uint256 _data ,uint256 _tokenId, uint256 _nonce, bytes calldata _signature) external {
		require(ownerOf(_tokenId) == msg.sender);
		require(syncNonces[_nonce]++ == _nonce);
		require(keccak256(abi.encodePacked(_tokenId, _nonce, _data)).toEthSignedMessageHash().recover(_signature) == signer, "Sig not valid");

		blobs[_tokenId] = _data;
	}

	function overrideTransfer(address from, address to, uint256 tokenId) external authorised(msg.sender) {
		_transfer(from, to, tokenId);
	}

	function overrideTransferWithSignature(
		address from,
		address to,
		uint256 tokenId,
		uint256 _nonce,
		bytes calldata _signature) external {
		require(ownerOf(tokenId) == msg.sender);
		require(transferNonces[tokenId]++ == _nonce);
		require(keccak256(abi.encodePacked(tokenId, _nonce)).toEthSignedMessageHash().recover(_signature) == signer, "Sig not valid");

		_transfer(from, to, tokenId);
	}

	function mintWithSignature(uint256 _nonce, bytes calldata _signature) external {
		require(balanceOf(msg.sender) == 0);
		require(mintNonces[msg.sender]++ == _nonce);
		require(keccak256(abi.encodePacked(msg.sender, _nonce)).toEthSignedMessageHash().recover(_signature) == signer, "Sig not valid");
		
		_mint(msg.sender, ++counter);
	}

	function burnWithSignature( uint256 tokenId, uint256 _nonce, bytes calldata _signature) external {
		require(ownerOf(tokenId) == msg.sender); // not necessary?
		require(burnNonces[tokenId]++ == _nonce);
		require(keccak256(abi.encodePacked(tokenId, _nonce)).toEthSignedMessageHash().recover(_signature) == signer, "Sig not valid");
		
		blobs[tokenId] = 0;
		_burn(tokenId);
	}

	function transferFrom(address from, address to, uint256 tokenId) public override {
		revert("nope");
	}

	function safeTransferFrom(address from, address to, uint256 tokenId) public override {
		revert("nope");
	}

	function safeTransferFrom(address from, address to, uint256 tokenId, bytes memory _data) public override {
		revert("nope");
	}
}