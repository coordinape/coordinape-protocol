pragma solidity ^0.8.2;

import {VaultAPI, BaseWrapper, RegistryAPI} from "wrapper/BaseWrapper.sol";
import {ApeVaultFactory} from "wrapper/ApeVaultFactory.sol";
import {ApeVault} from "wrapper/ApeVault.sol";
import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";

contract ApeRouter {

	uint256 constant MAX_UINT = type(uint256).max;

	address public yearnRegistry;
	address public apeVaultFactory;

	constructor(address _reg, address _factory) {
		yearnRegistry = _reg;
		apeVaultFactory = _factory;
	}

	event DepositInVault(address indexed vault, address token, uint256 amount);

	function delegateDeposit(address _apeVault, address _token, uint256 _amount) external {
		VaultsAPI vault = RegistryAPI(yearnRegistry).latestVault(_token);
		require(address(vault) != address(0), "ApeRouter: No vault for token");
		require(ApeVaultFactory(apeVaultFactory).vaultRegistry(_apeVault), "ApeRouter: Vault does not exist");

        IERC20(_token).safeTransferFrom(msg.sender, address(this), _amount);


		if (IERC20(_token).allowance(address(this), address(vault)) < _amount) {
            IERC20(_token).safeApprove(address(vault), 0); // Avoid issues with some IERC20(_token)s requiring 0
            IERC20(_token).safeApprove(address(vault), MAX_UINT); // Vaults are trusted
        }

		uint256 beforeBal = IERC20(_token).balanceOf(address(this));
        
		vault.deposit(_amount, _apeVault);

        uint256 afterBal = IERC20(_token).balanceOf(address(this));
        deposited = beforeBal.sub(afterBal);
        // `receiver` now has shares of `_bestVault` as balance, converted to `token` here
        // Issue a refund if not everything was deposited
        if (depositor != address(this) && afterBal > 0) IERC20(_token).safeTransfer(depositor, afterBal);
		ApeVault(_apeVault).addFunds(_amount);
		emit DepositInVault(_apeVault, _token, _amount);
	}

	 /**
     * @notice
     *  Used to update the yearn registry.
     * @param _registry The new _registry address.
     */
    function setRegistry(address _registry) external {
        require(msg.sender == registry.governance());
        // In case you want to override the registry instead of re-deploying
        registry = RegistryAPI(_registry);
        // Make sure there's no change in governance
        // NOTE: Also avoid bricking the wrapper from setting a bad registry
        require(msg.sender == registry.governance());
    }
}