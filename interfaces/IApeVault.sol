pragma solidity ^0.8.2;

interface IApeVault {
	function approveCircle(address _circle) external;
	function tap(uint256 _tapValue, uint8 _type) external;
}