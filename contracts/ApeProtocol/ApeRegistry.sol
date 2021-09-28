pragma solidity ^0.8.2;

import "@openzeppelin/contracts/access/Ownable.sol";

contract ApeRegistry is Ownable {
	address public feeRegistry;
	address public router;
	address public distributor;
	address public factory;

	function setFeeRegistry(address _registry) external onlyOwner {
		feeRegistry = _registry;
	}

	function setRouter(address _router) external onlyOwner {
		router = _router;
	}

	function setDistributor(address _distributor) external onlyOwner {
		distributor = _distributor;
	}

	function setFactory(address _factory) external onlyOwner {
		factory = _factory;
	}
}