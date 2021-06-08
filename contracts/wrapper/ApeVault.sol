pragma solidity ^0.8.2;

import "./AffiliateToken.sol";
import {VaultAPI, RegistryAPI} from "./BaseWrapper.sol";

contract ApeVaultWrapper is AffiliateToken {

	uint256 underlyingValue;
	address distributor;
	VaultAPI vault;

	constructor(
		address _distributor,
	    address _token,
        address _registry,
        string memory name,
        string memory symbol) BaseWrapper(_token, _registry) ERC20(name, symbol) {
		distributor = _distributor;
		vault = RegistryAPI(_registry).latestVault(_token);
	}

	function apeDeposit() external {
		apeDeposit(type(uint256).max);
	}

	function apeDeposit(uint256 _amount) external {
		underlyingValue += _amount;
		_deposit(msg.sender, address(this), amount, true);
	}

	function profit() public view returns {
		return _shareValue(token.balanceOf(address(this))) - underlyingValue;
	}

	// internal for now, depending whether contract is inherited or external
	function _tapOnlyProfitUnderlying(uint256 _tapValue) internal {
		require(_tapValue <= profit(), "Not enough profit to cover epoch");
		// naive implementation, we would probably need to make a call to the distributor
		// to make the token transfer happen from the distributor's context
		uint256 withdrawn = _withdraw(address(this), distributor, _sharesForValue(_tapValue), true);
		token.transfer(distributor, withdrawn);
	}

	function _tapOnlyProfit(uint256 _tapValue) internal {
		require(_tapValue <= profit(), "Not enough profit to cover epoch");
		vault.transfer(distributor, _sharesForValue(_tapValue));
	}

	function _tap(uint256 _tapValue) internal {
		require(_tapValue <= _shareValue(token.balanceOf(address(this))),
			"Not enough funds to cover epoch");
		uint256 remainder = _tapValue - profit();
		underlyingValue -= remainder;
		vault.transfer(distributor, _sharesForValue(_tapValue));
	}

	function _syncUnderlying() internal {
		underlyingValue = _shareValue(token.balanceOf(address(this)));
	}

}