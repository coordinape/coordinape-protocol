pragma solidity ^0.8.2;

import "./ApeVault.sol";

contract ApeVaultFactory {
	mapping(address => bool) public vaultRegistry;

	address public yearnRegistry;
	address public apeRouter;
	address public apeDistributor;

	event VaultCreated(address vault);

	constructor(address _reg, address _distro, address _router) {
		apeDistributor = _distro;
		yearnRegistry = _reg;
		apeRouter = _router;
	}

	function createApeVault(address _token, address _simpleToken) external {
		ApeVaultWrapper vault = new ApeVaultWrapper(apeDistributor, _token, yearnRegistry, apeRouter, _simpleToken);
		vault.transferOwnership(msg.sender);
		vaultRegistry[address(vault)] = true;
		emit VaultCreated(address(vault));
	}
}