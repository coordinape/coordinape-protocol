// SPDX-License-Identifier: MIT

pragma solidity ^0.8.2;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

import "./Coordinape.sol";
import "./CoordinapeEpoch.sol";

contract CoordinapeCircle is ERC721, Ownable {
    using Counters for Counters.Counter;

    Counters.Counter private _inviteIds;
    mapping(address => uint256) private _invites;
    mapping(uint256 => uint8) private _invitePermissions;

    Counters.Counter private _inviteBurned;

    Counters.Counter private _epochIds;
    mapping(uint256 => address) private _epochs;

    uint256 private _minimumVouches = 2**256 - 1;
    mapping(address => uint256) private _vouches;
    mapping(address => mapping(address => bool)) private _vouchedFor;

    event EpochCreated(uint256 indexed id, address epoch, uint256 end);
    event VouchCreated(address indexed recipient, address indexed sender);
    event InviteIssued(address indexed recipient, uint8 permissions);
    event InviteRevoked(address indexed recipient);

    constructor(string memory name, string memory id) ERC721(name, id) {}

    function invite(address recipient) public onlyOwner {
        require(balanceOf(recipient) == 0, "recipient is already invited.");
        _vouches[recipient] = _minimumVouches;
        _issueInvite(recipient, Coordinape.PARTICIPANT | Coordinape.RECEIVING);
    }

    function inviteNonReceiving(address recipient) public onlyOwner {
        require(balanceOf(recipient) == 0, "recipient is already invited.");
        _vouches[recipient] = _minimumVouches;
        _issueInvite(recipient, Coordinape.PARTICIPANT);
    }

    function revoke(address recipient) public onlyOwner {
        require(balanceOf(recipient) >= 1, "recipient is not invited.");
        _revokeInvite(recipient);
    }

    function edit(address recipient, uint8 permissions) public onlyOwner {
        require(balanceOf(recipient) >= 1, "recipient is not invited.");
        require(permissions != Coordinape.EXTERNAL, "call revoke to remove user.");
        uint256 inviteId = _invites[recipient];
        _invitePermissions[inviteId] = permissions;
    }

    function setMinimumVouches(uint256 value) public onlyOwner {
        _minimumVouches = value;
    }

    function startEpoch(uint256 amount, uint256 end) public onlyOwner returns (address epoch) {
        require(!_epochInProgress(), "another epoch is already in progress.");
        require(block.number < end, "end block must be in the future.");

        bytes memory creationCode = type(CoordinapeEpoch).creationCode;
        bytes memory bytecode = abi.encodePacked(creationCode, abi.encode(amount, end));

        Counters.increment(_epochIds);
        uint256 epochId = Counters.current(_epochIds);
        bytes32 salt = keccak256(abi.encodePacked(name(), symbol(), epochId));
        assembly {
            epoch := create2(0, add(bytecode, 32), mload(bytecode), salt)
        }
        _epochs[epochId] = epoch;
        emit EpochCreated(epochId, epoch, end);
        return epoch;
    }

    function joinCurrentEpoch() public onlyInvited onlyInProgress {
        CoordinapeEpoch epoch = CoordinapeEpoch(currentEpochAddress());
        uint256 tokenId = _invites[_msgSender()];
        uint8 permissions = _invitePermissions[tokenId];
        epoch.addParticipant(_msgSender(), permissions);
    }

    function leaveCurrentEpoch() public onlyInvited onlyInProgress {
        CoordinapeEpoch epoch = CoordinapeEpoch(currentEpochAddress());
        epoch.freezePartecipant(_msgSender());
    }

    function vouch(address recipient) public onlyInvited {
        require(balanceOf(recipient) == 0, "recipient is already invited.");
        require(!_vouchedFor[_msgSender()][recipient], "sender already vouched for recipient.");
        _vouches[recipient] += 1;
        _vouchedFor[_msgSender()][recipient] = true;
        emit VouchCreated(recipient, _msgSender());
    }

    function enter() public {
        require(balanceOf(_msgSender()) == 0, "sender is already invited.");
        require(_vouches[_msgSender()] >= _minimumVouches, "sender didn't receive minimum vouches.");
        _issueInvite(_msgSender(), Coordinape.PARTICIPANT | Coordinape.RECEIVING);
    }

    function enterNonReceiving() public {
        require(balanceOf(_msgSender()) == 0, "sender is already invited.");
        require(_vouches[_msgSender()] >= _minimumVouches, "sender didn't receive minimum vouches.");
        _issueInvite(_msgSender(), Coordinape.PARTICIPANT);
    }

    function inviteOf(address recipient) public view returns (uint256) {
        return _invites[recipient];
    }

    function permissionsOf(address recipient) public view returns (uint8) {
        return _invitePermissions[inviteOf(recipient)];
    }

    function vouchesOf(address recipient) public view returns (uint256) {
        return _vouches[recipient];
    }

    function minimumVouches() public view returns (uint256) {
        return _minimumVouches;
    }

    function currentEpochAddress() public view returns (address) {
        return epochAddress(currentEpochId());
    }

    function currentEpochId() public view returns (uint256) {
        return Counters.current(_epochIds);
    }

    function epochAddress(uint256 id) public view returns (address) {
        return _epochs[id];
    }

    function _epochInProgress() internal view returns (bool) {
        uint256 epochId = Counters.current(_epochIds);
        return epochId > 0 && !CoordinapeEpoch(_epochs[epochId]).ended();
    }

    function _issueInvite(address recipient, uint8 permissions) internal {
        Counters.increment(_inviteIds);
        uint256 tokenId = Counters.current(_inviteIds);
        _mint(recipient, tokenId);
        _invitePermissions[tokenId] = permissions;
        _invites[recipient] = tokenId;
        _vouches[recipient] = 0;
        emit InviteIssued(recipient, permissions);
    }

    function _revokeInvite(address recipient) internal {
        uint256 tokenId = _invites[recipient];
        _burn(tokenId);
        _invitePermissions[tokenId] = 0;
        _invites[recipient] = 0;
        emit InviteRevoked(recipient);
    }

    modifier onlyInvited() {
        require(balanceOf(_msgSender()) >= 1, "method can only be called by an invited user.");
        _;
    }

    modifier onlyInProgress() {
        require(_epochInProgress(), "no epoch currently in progress.");
        _;
    }

    function totalSupply() public view returns (uint256) {
        return Counters.current(_inviteIds) - Counters.current(_inviteBurned);
    }

    function _beforeTokenTransfer(
        address sender,
        address recipient,
        uint256 tokenId
    ) internal override {
        require(recipient == address(0) || balanceOf(recipient) == 0, "recipient is already invited.");
        require(
            recipient == address(0) || _vouches[recipient] >= _minimumVouches,
            "recipient didn't receive minimum vouches."
        );
        _invites[sender] = 0;
        _invites[recipient] = tokenId;
        if (recipient == address(0)) {
            Counters.increment(_inviteBurned);
        }
    }
}
