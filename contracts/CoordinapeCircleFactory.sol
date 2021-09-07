// SPDX-License-Identifier: MIT

pragma solidity ^0.8.2;

import "@openzeppelin/contracts/proxy/Clones.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

import "../interfaces/ICoordinapeCircle.sol";

contract CoordinapeCircleFactory is Ownable {
    using Clones for address;

    address private _coordinapeCircleImp;
    mapping(bytes32 => address) public circles;
    address[] public allCircles;

    event CoordinapeCircleCreation(bytes32 circleHash, address circle);

    constructor(address imp) {
        _coordinapeCircleImp = imp;
    }

    /*
     *  Admin functions
     */
    function setCoordinapeCircleImp(address imp) external onlyOwner {
        _coordinapeCircleImp = imp;
    }

    /*
     *  View functions
     */
    function coordinapeCircleImp() external view returns (address) {
        return _coordinapeCircleImp;
    }

    /*
     *  Create functions
     */
    function createCoordinapeCircleImp(
        string memory name,
        string memory id,
        string memory uri,
        uint256 minimumV
    ) external returns (address newCoordinapeCircle) {
        bytes32 cHash = keccak256(abi.encodePacked(msg.sender, name, id));
        newCoordinapeCircle = _coordinapeCircleImp.cloneDeterministic(cHash);

        ICoordinapeCircle(newCoordinapeCircle).initialize(_msgSender(), name, id, uri, minimumV);

        circles[cHash] = newCoordinapeCircle;
        allCircles.push(newCoordinapeCircle);

        emit CoordinapeCircleCreation(cHash, newCoordinapeCircle);
    }
}
