pragma solidity ^0.8.2;

import "@openzeppelin/contracts/proxy/beacon/BeaconProxy.sol";

contract ApeBeacon is BeaconProxy {

	constructor(address _apeBeacon, bytes memory data) BeaconProxy(_apeBeacon, data) {}
}