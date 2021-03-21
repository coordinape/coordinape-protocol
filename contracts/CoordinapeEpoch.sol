// SPDX-License-Identifier: MIT

pragma solidity ^0.8.2;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract CoordinapeEpoch is ERC20, Ownable {
    uint256 _start;
    uint256 _end;

    uint8 public constant EXTERNAL = 0; // 00
    uint8 public constant PARTICIPANT = 1; // 01
    uint8 public constant NON_RECEIVING = 2; // 10

    mapping(address => uint8) _participants;
    mapping(address => mapping(address => string)) _notes;

    uint256 _amount;

    constructor(uint256 amount, uint256 end) ERC20("Give", "GIVE") {
        require(
            block.number < end,
            "CoordinapeEpoch: end block must be in the future."
        );
        _amount = amount;
        _start = block.number;
        _end = end;
    }

    function addParticipant(address user) public onlyOwner {
        require(
            _participants[user] == EXTERNAL,
            "CoordinapeEpoch: user is already a participant."
        );
        _alter(user, PARTICIPANT);
        _mint(user, _amount);
    }

    function addParticipantNonReceiving(address user) public onlyOwner {
        require(
            _participants[user] == EXTERNAL,
            "CoordinapeEpoch: user is already a participant."
        );
        _alter(user, PARTICIPANT | NON_RECEIVING);
        _mint(user, _amount);
    }

    function removeParticipant(address user) public onlyOwner {
        require(
            _participants[user] > EXTERNAL,
            "CoordinapeEpoch: user is not participant."
        );
        _alter(user, EXTERNAL);
    }

    function addNote(address recipient, string memory note)
        public
        onlyParticipant
        beforeEnd
    {
        require(
            _participants[recipient] > EXTERNAL,
            "CoordinapeEpoch: user is already a participant."
        );
        require(
            _msgSender() != recipient,
            "CoordinapeEpoch: cannot add a note to self."
        );
        _notes[recipient][_msgSender()] = note;
    }

    function leave() public onlyParticipant {
        require(
            _participants[_msgSender()] != EXTERNAL,
            "CoordinapeEpoch: user is already not a participant."
        );
        _alter(_msgSender(), EXTERNAL);
    }

    function stopReceiving() public onlyParticipant {
        require(
            (_participants[_msgSender()] & NON_RECEIVING) != 0,
            "CoordinapeEpoch: user is already a non-receiving participant."
        );
        _alter(_msgSender(), PARTICIPANT | NON_RECEIVING);
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

    function decimals() public pure override returns (uint8) {
        return 0;
    }

    modifier onlyParticipant() {
        require(
            (_participants[_msgSender()] & PARTICIPANT) != 0,
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

    function transfer(address recipient, uint256 amount)
        public
        override
        onlyParticipant
        beforeEnd
        returns (bool)
    {
        require(
            (_participants[_msgSender()] & PARTICIPANT) != 0 &&
                (_participants[_msgSender()] & NON_RECEIVING) == 0,
            "CoordinapeEpoch: recipient must be a participant"
        );
        return super.transfer(recipient, amount);
    }

    function transferFrom(
        address sender,
        address recipient,
        uint256 amount
    ) public virtual override beforeEnd returns (bool) {
        require(
            (_participants[_msgSender()] & PARTICIPANT) != 0,
            "CoordinapeEpoch: sender must be a participant"
        );
        require(
            (_participants[_msgSender()] & PARTICIPANT) != 0 &&
                (_participants[_msgSender()] & NON_RECEIVING) == 0,
            "CoordinapeEpoch: recipient must be a participant"
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
