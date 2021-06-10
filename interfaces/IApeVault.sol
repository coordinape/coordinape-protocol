pragma solidity ^0.8.2;

interface IApeVault {
	function tapOnlyProfitUnderlying(uint256 _tapValue, uint256 _slippage) external;

	function tapOnlyProfit(uint256 _tapValue) external;

	function tap(uint256 _tapValue) external;
}