pragma solidity ^0.8.2;

import "./ApeVault.sol";

contract ApeVaultFactory {
	mapping(address => bool) public vaultRegistry;

	address public yearnRegistry;
	address public apeDistributor;

	event VaultCreated(address vault)

	constructor(address _reg, address _distro) {
		apeDistributor = _distro;
		yearnRegistry = _reg;
	}

	function createApeVault(address _token, address _simpleToken) external {
		ApeVault vault = new ApeVault(apeDistributor, _token, yearnRegistry, _simpleToken);
		vault.transferOwnership(msg.sender);
		vaultRegistry[address(vault)] = true;
		emit VaultCreated(address(vault));
}