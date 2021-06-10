pragma solidity ^0.8.2;

import "@openzeppelin/contracts/access/Ownable.sol";
import "../../interfaces/IApeVault.sol";

import "./BaseWrapper.sol";

contract ApeVaultWrapper is BaseWrapper, Ownable, IApeVault {
	using SafeERC20 for IERC20;
	uint256 underlyingValue;
	address distributor;
	VaultAPI vault;

	constructor(
		address _distributor,
	    address _token,
        address _registry,
        string memory name,
        string memory symbol) BaseWrapper(_token, _registry) {
		distributor = _distributor;
		vault = VaultAPI(RegistryAPI(_registry).latestVault(_token));
	}

	modifier onlyDistributor() {
		require(msg.sender == distributor);
		_;
	}

	function _shareValue(uint256 numShares) internal view returns (uint256) {
		return vault.pricePerShare() * numShares / 1e18;
    }

    function _sharesForValue(uint256 amount) internal view returns (uint256) {
		return amount * 1e18 / vault.pricePerShare();
    }

	function profit() public view returns(uint256) {
		return _shareValue(token.balanceOf(address(this))) - underlyingValue;
	}

	function apeDeposit(uint256 _amount) public {
		underlyingValue += _amount;
		_deposit(msg.sender, address(this), _amount, true);
	}

	// if we include slippage in tapping functions, the fraction of tokens will add up
	// adding this function to allow depositing of dust when it comes large enough
	function apeDepositDust() external {
		uint256 amount = token.balanceOf(address(this));
		token.safeApprove(address(vault), 0);
		token.safeApprove(address(vault), amount);
		_deposit(address(this), address(this), amount, true);
	}

	function apeDeposit() external {
		apeDeposit(type(uint256).max);
	}

	function apeMigrate() external onlyOwner {
		_migrate(address(this));
		vault = VaultAPI(registry.latestVault(address(token)));
	}

	function tapOnlyProfitUnderlying(uint256 _tapValue, uint256 _slippage) external override onlyDistributor {
		require(_tapValue <= profit(), "Not enough profit to cover epoch");
		uint256 shares = _sharesForValue(_tapValue) * _slippage / 10000;
		uint256 withdrawn = _withdraw(address(this), distributor, shares, true);
		require(withdrawn >= _tapValue, "Withdrawal returned less than expected");
		token.transfer(distributor, _tapValue);
	}

	function tapOnlyProfit(uint256 _tapValue) external override onlyDistributor {
		require(_tapValue <= profit(), "Not enough profit to cover epoch");
		vault.safeTransfer(distributor, _sharesForValue(_tapValue));
	}

	function tap(uint256 _tapValue) external override onlyDistributor {
		require(_tapValue <= _shareValue(token.balanceOf(address(this))),
			"Not enough funds to cover epoch");
		uint256 remainder = _tapValue - profit();
		underlyingValue -= remainder;
		vault.safeTransfer(distributor, _sharesForValue(_tapValue));
	}

	function syncUnderlying() external onlyOwner {
		underlyingValue = _shareValue(token.balanceOf(address(this)));
	}

}