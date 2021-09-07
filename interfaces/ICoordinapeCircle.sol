pragma solidity ^0.8.2;

interface ICoordinapeCircle {
    function initialize(
        address owner,
        string memory name,
        string memory id,
        string memory uri,
        uint256 _minimumV
    ) external returns (bool);
}
