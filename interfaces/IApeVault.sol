pragma solidity ^0.8.2;

interface IApeVault {
	function tap(uint256 _tapValue, uint8 _type) external;
}