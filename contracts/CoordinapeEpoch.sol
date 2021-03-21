// SPDX-License-Identifier: MIT

pragma solidity ^0.8.2;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

import "./Coordinape.sol";

contract CoordinapeEpoch is ERC20, Ownable {
    uint256 private _start;
    uint256 private _end;

    mapping(address => uint8) private _participants;
    mapping(address => mapping(address => string)) private _notes;

    uint256 private _amount;

    constructor(uint256 amount, uint256 end) ERC20("Give", "GIVE") {
        require(
            block.number < end,
            "CoordinapeEpoch: end block must be in the future."
        );
        _amount = amount;
        _start = block.number;
        _end = end;
    }

    function addParticipant(address user, uint8 permissions) public onlyOwner {
        require(
            permissions & Coordinape.PARTICIPANT != 0,
            "CoordinapeEpoch: permissions must contain 'PARTECIPANT'."
        );
        require(
            _participants[user] == Coordinape.EXTERNAL,
            "CoordinapeEpoch: user is already a participant."
        );
        _alter(user, permissions);
        _mint(user, _amount);
    }

    function removeParticipant(address user) public onlyOwner {
        require(
            _participants[_msgSender()] & Coordinape.PARTICIPANT != 0,
            "CoordinapeEpoch: user is already not a participant."
        );
        _alter(user, Coordinape.EXTERNAL);
    }

    function addNote(address recipient, string memory note)
        public
        onlyParticipant
        beforeEnd
    {
        require(
            _participants[recipient] & Coordinape.PARTICIPANT != 0,
            "CoordinapeEpoch: recipient is not a participant."
        );
        require(
            _msgSender() != recipient,
            "CoordinapeEpoch: cannot add a note to self."
        );
        _notes[recipient][_msgSender()] = note;
    }

    function stopReceiving() public onlyParticipant {
        require(
            _participants[_msgSender()] & Coordinape.RECEIVING != 0,
            "CoordinapeEpoch: user is already a non-receiving participant."
        );
        _alter(_msgSender(), Coordinape.PARTICIPANT);
    }

    function leave() public onlyParticipant {
        stopReceiving();
        _burn(_msgSender(), balanceOf(_msgSender()));
    }

    function permissionsOf(address user) public view returns (uint8) {
        return _participants[user];
    }

    function isParticipant(address user) public view returns (bool) {
        return _participants[user] & Coordinape.PARTICIPANT != 0;
    }

    function startBlock() public view returns (uint256) {
        return _start;
    }

    function endBlock() public view returns (uint256) {
        return _end;
    }

    function ended() public view returns (bool) {
        return block.number >= _end;
    }

    function _alter(address user, uint8 role) internal {
        require(
            role != _participants[user],
            "CoordinapeEpoch: user state unchanged."
        );
        _participants[user] = role;
    }

    modifier onlyParticipant() {
        require(
            _participants[_msgSender()] & Coordinape.PARTICIPANT != 0,
            "CoordinapeEpoch: method can only be called by a registered participant."
        );
        _;
    }

    modifier beforeEnd() {
        require(
            !ended(),
            "CoordinapeEpoch: method can only be called before the end of the epoch."
        );
        _;
    }

    modifier afterEnd() {
        require(
            ended(),
            "CoordinapeEpoch: method can only be called after the end of the epoch."
        );
        _;
    }

    function decimals() public pure override returns (uint8) {
        return 0;
    }

    function transfer(address recipient, uint256 amount)
        public
        override
        onlyParticipant
        beforeEnd
        returns (bool)
    {
        require(
            (_participants[_msgSender()] & Coordinape.PARTICIPANT) != 0 &&
                (_participants[_msgSender()] & Coordinape.RECEIVING) != 0,
            "CoordinapeEpoch: recipient must be a receiving participant"
        );
        return super.transfer(recipient, amount);
    }

    function transferFrom(
        address sender,
        address recipient,
        uint256 amount
    ) public virtual override beforeEnd returns (bool) {
        require(
            (_participants[_msgSender()] & Coordinape.PARTICIPANT) != 0,
            "CoordinapeEpoch: sender must be a participant"
        );
        require(
            (_participants[_msgSender()] & Coordinape.PARTICIPANT) != 0 &&
                (_participants[_msgSender()] & Coordinape.RECEIVING) != 0,
            "CoordinapeEpoch: recipient must be a receiving participant"
        );
        return super.transferFrom(sender, recipient, amount);
    }

    function approve(address spender, uint256 amount)
        public
        override
        onlyParticipant
        beforeEnd
        returns (bool)
    {
        return super.approve(spender, amount);
    }

    function increaseAllowance(address spender, uint256 addedValue)
        public
        override
        onlyParticipant
        beforeEnd
        returns (bool)
    {
        return super.increaseAllowance(spender, addedValue);
    }

    function decreaseAllowance(address spender, uint256 subtractedValue)
        public
        override
        onlyParticipant
        beforeEnd
        returns (bool)
    {
        return super.decreaseAllowance(spender, subtractedValue);
    }
}
