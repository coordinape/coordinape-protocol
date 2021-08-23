pragma solidity ^0.8.2;

import "@openzeppelin/contracts/access/Ownable.sol";
import "../../interfaces/IApeVault.sol";
import "../ApeDistributor.sol";
import "../ApeAllowanceModule.sol";

import "./BaseWrapper.sol";

contract ApeVaultWrapper is BaseWrapper, Ownable, IApeVault {
	using SafeERC20 for VaultAPI;
	using SafeERC20 for IERC20;

	uint256 constant TOTAL_SHARES = 10000;
	
	IERC20 public simpleToken;

	uint256 underlyingValue;
	address distributor;
	address router;
	VaultAPI public vault;
	ApeAllowanceModule public allowanceModule;

	constructor(
		address _distributor,
	    address _token,
        address _registry,
		address _router,
		address _simpleToken) BaseWrapper(_token, _registry) {
		distributor = _distributor;
		vault = VaultAPI(RegistryAPI(_registry).latestVault(_token));
		simpleToken = IERC20(_simpleToken);
		router = _router;
	}

	event ApeVaultFundWithdrawal(address indexed apeVault, address vault, uint256 _amount);

	modifier onlyDistributor() {
		require(msg.sender == distributor);
		_;
	}

	modifier onlyRouter() {
		require(msg.sender == router);
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

	function apeDepositSimpleToken(uint256 _amount) public {
		simpleToken.safeTransferFrom(msg.sender, address(this), _amount);
	}


	// TODO
	// add withdraw
	// add simple token interaction

	// if we include slippage in tapping functions, the fraction of tokens will add up
	// adding this function to allow depositing of dust when it becomes large enough
	function apeDepositDust() external {
		uint256 amount = token.balanceOf(address(this));
		underlyingValue += amount;
		token.safeApprove(address(vault), 0);
		token.safeApprove(address(vault), amount);
		_deposit(address(this), address(this), amount, true);
	}

	function apeDeposit() external {
		apeDeposit(token.balanceOf(msg.sender));
	}

	//wip
	function apeWithdrawUnderlying(uint256 _underlyingAmount) external onlyOwner {
		uint256 total = _shareValue(token.balanceOf(address(this)));
		require(_underlyingAmount <= underlyingValue, "underlying amount higher than vault value");

		underlyingValue -= _underlyingAmount;
		uint256 shares = _sharesForValue(_underlyingAmount);
		uint256 withdrawn = _withdraw(address(this), msg.sender, shares, true);
		emit ApeVaultFundWithdrawal(address(this), address(vault), shares);
	}

	function exitVaultToken() external onlyOwner {
		underlyingValue = 0;
		uint256 totalShares = vault.balanceOf(address(this))
		vault.transfer(msg.sender, totalShares);
		emit ApeVaultFundWithdrawal(address(this), address(vault), totalShares);
	}

	function apeMigrate() external onlyOwner {
		_migrate(address(this));
		vault = VaultAPI(registry.latestVault(address(token)));
	}

	function tap(uint256 _value, uint256 _slippage, uint8 _type) external override onlyDistributor {
		if (_type == uint8(0))
			_tapOnlyProfitUnderlying(_value, _slippage);
		else if (_type == uint8(1))
			_tapOnlyProfit(_value);
		else if (_type == uint8(2))
			_tapBase(_value);
		else if (_type == uint8(3))
			_tapSimpleToken(_value);
	}

	function _tapOnlyProfitUnderlying(uint256 _tapValueUnderlying, uint256 _slippage) internal {
		require(_tapValueUnderlying <= profit(), "Not enough profit to cover epoch");
		uint256 shares = _sharesForValue(_tapValueUnderlying) * (10000 * _slippage) / 10000;
		uint256 withdrawn = _withdraw(address(this), distributor, shares, true);
		require(withdrawn >= _tapValueUnderlying, "Withdrawal returned less than expected");
		token.transfer(distributor, _tapValueUnderlying);
	}

	// _tapValue is vault token amount to remove
	function _tapOnlyProfit(uint256 _tapValue) internal {
		require(_shareValue(_tapValue) <= profit(), "Not enough profit to cover epoch");
		vault.safeTransfer(distributor, _tapValue);
	}

	function _tapBase(uint256 _tapValue) internal {
		int256 remainder = int256(_shareValue(_tapValue)) - int256(profit());
		if (remainder > 0)
			underlyingValue -= uint256(remainder);
		vault.safeTransfer(distributor, _tapValue);
	}

	function _tapSimpleToken(uint256 _tapValue) internal {
		uint256 fee = _tapValue * ApeDistributor(distributor).tierCFee() / TOTAL_SHARES;
		simpleToken.transfer(distributor, _tapValue + fee);
	}

	function syncUnderlying() external onlyOwner {
		underlyingValue = _shareValue(token.balanceOf(address(this)));
	}

	function addFunds(uint256 _amount) external onlyRouter {
		underlyingValue += _amount;
	}

	function updateCircle(address _circle, bool _value) external onlyOwner {
		ApeDistributor(distributor).updateCircleToVault(_circle, _value);
	}

	function approveCircleAdmin(address _circle, address _admin) external onlyOwner {
		ApeDistributor(distributor).updateCircleAdmin(_circle, _admin);
	}



	function updateAllowance(
		address _circle,
		address _token,
		uint256 _amount,
		uint256 _interval
		) external onlyOwner {
		ApeDistributor(distributor).setAllowance(_circle, _token, _amount, _interval);
	}
}