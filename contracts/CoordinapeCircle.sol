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

    Counters.Counter private _epochIds;
    mapping(uint256 => address) private _epochs;

    uint8 public constant MINIMUM_VOUCHES = 2;
    mapping(address => uint256) private _vouches;

    event EpochCreated(uint256 indexed id, address epoch, uint256 end);

    constructor(string memory name, string memory id) ERC721(name, id) {}

    function invite(address recipient) public onlyOwner {
        require(
            balanceOf(recipient) == 0,
            "CoordinapeCircle: recipient is already invited."
        );
        _vouches[recipient] = MINIMUM_VOUCHES;
        Counters.increment(_inviteIds);
        _issueInvite(
            recipient,
            Counters.current(_inviteIds),
            Coordinape.PARTICIPANT | Coordinape.RECEIVING
        );
    }

    function inviteNonReceiving(address recipient) public onlyOwner {
        require(
            balanceOf(recipient) == 0,
            "CoordinapeCircle: recipient is already invited."
        );
        _vouches[recipient] = MINIMUM_VOUCHES;
        Counters.increment(_inviteIds);
        _issueInvite(
            recipient,
            Counters.current(_inviteIds),
            Coordinape.PARTICIPANT
        );
    }

    function enter() public {
        require(
            balanceOf(_msgSender()) == 0,
            "CoordinapeCircle: sender is already invited."
        );
        require(
            _vouches[_msgSender()] >= MINIMUM_VOUCHES,
            "CoordinapeCircle: sender didn't receive MINIMUM_VOUCHES."
        );
        Counters.increment(_inviteIds);
        _issueInvite(
            _msgSender(),
            Counters.current(_inviteIds),
            Coordinape.PARTICIPANT | Coordinape.RECEIVING
        );
    }

    function enterNonReceiving() public {
        require(
            balanceOf(_msgSender()) == 0,
            "CoordinapeCircle: sender is already invited."
        );
        require(
            _vouches[_msgSender()] >= MINIMUM_VOUCHES,
            "CoordinapeCircle: sender didn't receive MINIMUM_VOUCHES."
        );
        Counters.increment(_inviteIds);
        _issueInvite(
            _msgSender(),
            Counters.current(_inviteIds),
            Coordinape.PARTICIPANT
        );
    }

    function joinCurrentEpoch() public onlyInvited {
        uint256 epochId = Counters.current(_epochIds);
        require(
            epochId > 0 && !CoordinapeEpoch(_epochs[epochId]).ended(),
            "CoordinapeCircle: no epoch currently in progress."
        );
        CoordinapeEpoch epoch = CoordinapeEpoch(_epochs[epochId]);
        uint256 tokenId = _invites[_msgSender()];
        uint8 permissions = _invitePermissions[tokenId];
        epoch.addParticipant(_msgSender(), permissions);
    }

    function startEpoch(uint256 amount, uint256 end)
        public
        onlyOwner
        returns (address epoch)
    {
        require(
            Counters.current(_epochIds) == 0 ||
                CoordinapeEpoch(_epochs[Counters.current(_epochIds)]).ended(),
            "CoordinapeCircle: another epoch is already in progress."
        );
        bytes memory creationCode = type(CoordinapeEpoch).creationCode;
        bytes memory bytecode =
            abi.encodePacked(creationCode, abi.encode(amount, end));
        Counters.increment(_epochIds);
        uint256 epochId = Counters.current(_epochIds);
        bytes32 salt = keccak256(abi.encodePacked(name(), symbol(), epochId));
        assembly {
            epoch := create2(0, add(bytecode, 32), mload(bytecode), salt)
        }
        _epochs[epochId] = epoch;
        emit EpochCreated(epochId, epoch, end);
    }

    function vouch(address recipient) public onlyInvited {
        require(
            balanceOf(recipient) == 1,
            "CoordinapeCircle: recipient is already invited."
        );
        _vouches[recipient] += 1;
    }

    function _issueInvite(
        address recipient,
        uint256 tokenId,
        uint8 permissions
    ) internal virtual {
        require(
            balanceOf(recipient) == 1,
            "CoordinapeCircle: recipient is already invited."
        );
        _mint(recipient, tokenId);
        _invitePermissions[tokenId] = permissions;
        _invites[recipient] = tokenId;
    }

    function _beforeTokenTransfer(
        address sender,
        address recipient,
        uint256 tokenId
    ) internal view override {
        require(
            balanceOf(recipient) == 0,
            "CoordinapeCircle: recipient is already invited."
        );
        require(
            _vouches[recipient] >= MINIMUM_VOUCHES,
            "CoordinapeCircle: recipient didn't receive MINIMUM_VOUCHES."
        );
    }

    modifier onlyInvited() {
        require(
            balanceOf(_msgSender()) >= 1,
            "CoordinapeCircle: method can only be called by an invited user."
        );
        _;
    }
}
