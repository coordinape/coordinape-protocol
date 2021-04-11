// SPDX-License-Identifier: MIT

pragma solidity ^0.8.2;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

import "./Coordinape.sol";
import "./CoordinapeEpoch.sol";
import "./CoordinapeTokenSet.sol";

contract CoordinapeCircle is ERC721, Ownable {
    using Counters for Counters.Counter;

    enum EpochState {
        CREATED,
        GIVE_DISTRIBUTED,
        FINALISED
    }

    Counters.Counter private _inviteIds;
    mapping(address => uint256) private _invites;
    mapping(uint256 => uint8) private _invitePermissions;

    Counters.Counter private _inactiveMembers;

    Counters.Counter private _epochIds;
    mapping(uint256 => uint256) private _epochEnds;
    mapping(uint256 => uint8) private _epochState;

    uint256 private _minimumVouches;
    mapping(address => uint256) private _vouches;
    mapping(address => mapping(address => bool)) private _vouchedFor;

    TokenSet public tokenSet;

    event EpochCreated(uint256 indexed id, uint256 end);
    event VouchCreated(address indexed recipient, address indexed sender);
    event InviteIssued(address indexed recipient, uint8 permissions);
    event InviteRevoked(address indexed recipient, uint8 permissions);

    string private _uri;

    constructor(
        string memory name,
        string memory id,
        string memory uri,
        uint256 _minimumV
    ) ERC721(name, id) {
        _uri = uri;
        _minimumVouches = _minimumV;
    }

    /*
     *  Admin functions
     */
    function invite(address recipient, uint8 _rights) external onlyOwner {
        require(balanceOf(recipient) == 0, "recipient is already invited.");
        require(_rights != 0, "rights cannot be none");
        _vouches[recipient] = _minimumVouches;
        _issueInvite(recipient, _rights);
    }

    // to consider, should we remove them from the epoch too?
    function revoke(address recipient) external onlyOwner {
        require(balanceOf(recipient) >= 1, "recipient is not invited.");
        _revokeInvite(recipient);
    }

    function edit(address recipient, uint8 permissions) external onlyOwner {
        require(balanceOf(recipient) >= 1, "recipient is not invited.");
        require(permissions != Coordinape.EXTERNAL, "call revoke to remove user.");
        require(
            permissions & Coordinape.PARTICIPANT != 0,
            "permissions must contain at least 'PARTICIPANT'."
        );
        uint256 tokenId = _invites[recipient];
        _invitePermissions[tokenId] = permissions;
    }

    function setMinimumVouches(uint256 value) external onlyOwner {
        _minimumVouches = value;
    }

    function setTokenSet(address _tokenSet) external onlyOwner {
        tokenSet = TokenSet(_tokenSet);
    }

    function startEpoch(uint256 amount, uint256 end, uint256 _grant) external onlyOwner {
        require(!_epochInProgress(), "another epoch is already in progress.");
        require(block.number < end, "end block must be in the future.");

        Counters.increment(_epochIds);
        uint256 epochId = Counters.current(_epochIds);
        //address epoch = address(new CoordinapeEpoch(amount, end));
        //_epochs[epochId] = epoch;
        _epochEnds[epochId] = end;
        _epochState[epochId] = uint8(EpochState.CREATED);
        tokenSet.startEpoch(epochId, amount, _grant);
        emit EpochCreated(epochId, end);
    }

    function sync(
		address _giver,
		address[] calldata _receivers,
		uint256[] calldata _alloc,
        bytes calldata _sig,
        bool _lastSync) external onlyOwner {
        require(block.number >= _epochEnds[_epochIds.current()], "Cannot sync yet");
        tokenSet.sync(_epochIds.current(), _giver, _receivers, _alloc, _sig);
        if (_lastSync)
            _epochState[_epochIds.current()] = uint8(EpochState.GIVE_DISTRIBUTED);
    }

    function finalise() external onlyOwner {
        require(_epochState[_epochIds.current()] == uint8(EpochState.GIVE_DISTRIBUTED), "Cannot finalise");
        _epochState[_epochIds.current()] = uint8(EpochState.FINALISED);
    }

    /*
     *  Member functions
     */
    function joinCurrentEpoch(bool _optOut) external onlyInvited onlyInProgress {
        uint256 tokenId = _invites[_msgSender()];
        uint8 permissions = _invitePermissions[tokenId];
        if (_optOut)
        {
            require(permissions & Coordinape.GIVER != 0, "Cannot optout if no givver rights");
            tokenSet.addParticipant(_epochIds.current(), _msgSender(), permissions & ~Coordinape.RECEIVER);
        }
        else
            tokenSet.addParticipant(_epochIds.current(), _msgSender(), permissions);
    }

    function leaveCurrentEpoch() external onlyInvited onlyInProgress {
        tokenSet.removeParticipant(_epochIds.current(), _msgSender());
    }

    function vouch(address recipient) external onlyInvited {
        require(balanceOf(recipient) == 0, "recipient is already invited.");
        require(!_vouchedFor[_msgSender()][recipient], "sender already vouched for recipient.");
        uint256 tokenId = _invites[_msgSender()];
        require(_invitePermissions[tokenId] & Coordinape.GIVER != 0, "sender cannot vouch");
        _vouches[recipient] += 1;
        _vouchedFor[_msgSender()][recipient] = true;
        emit VouchCreated(recipient, _msgSender());
    }

    function enter() external {
        require(balanceOf(_msgSender()) == 0, "sender is already invited.");
        require(
            _vouches[_msgSender()] >= _minimumVouches,
            "sender didn't receive minimum vouches."
        );
        _issueInvite(_msgSender(), Coordinape.PARTICIPANT);
    }

    function burn(address _getter, uint256 _amount) external {
        tokenSet.burnGet(_epochIds.current(), _getter, _amount);
    }

    /*
     *  View functions
     */

    function state(uint256 _epoch) external view returns(uint8) {
        return _epochState[_epoch];
    }

    function members() external view returns (address[] memory) {
        address[] memory addresses = new address[](activeMembersCount());
        uint256 j = 0;
        for (uint256 i = 1; i <= Counters.current(_inviteIds); i++) {
            if (_exists(i) && _invitePermissions[i] != 0) {
                address owner = ownerOf(i);
                addresses[j++] = owner;
            }
        }
        return addresses;
    }

    function activeMembersCount() public view returns (uint256) {
        return totalSupply();
    }

    function inviteOf(address recipient) public view returns (uint256) {
        return _invites[recipient];
    }

    function permissionsOf(address recipient) external view returns (uint8) {
        return _invitePermissions[inviteOf(recipient)];
    }

    function vouchesOf(address recipient) external view returns (uint256) {
        return _vouches[recipient];
    }

    function minimumVouches() external view returns (uint256) {
        return _minimumVouches;
    }

    // function currentEpochAddress() public view returns (address) {
    //     return epochAddress(currentEpochId());
    // }

    function currentEpochId() public view returns (uint256) {
        return Counters.current(_epochIds);
    }

    // function epochAddress(uint256 id) public view returns (address) {
    //     return _epochs[id];
    // }

    // should be totalActiveMembers
    function totalSupply() public view returns (uint256) {
        return Counters.current(_inviteIds) - _inactiveMembers.current();
    }


    /*
     *  Internal functions
     */
    function _epochInProgress() internal view returns (bool) {
        uint256 epochId = Counters.current(_epochIds);
        // return epochId > 0 && !CoordinapeEpoch(_epochs[epochId]).ended();
        return epochId > 0 && block.number < _epochEnds[epochId];
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
        _inactiveMembers.increment();
        //_burn(tokenId);
        _invitePermissions[tokenId] = 0;
        _invites[recipient] = 0;
        emit InviteRevoked(recipient, 0);
    }

    modifier onlyInvited() {
        require(balanceOf(_msgSender()) >= 1, "method can only be called by an invited user.");
        _;
    }

    modifier onlyInProgress() {
        require(_epochInProgress(), "no epoch currently in progress.");
        _;
    }

    function _baseURI() internal view override returns (string memory) {
        return _uri;
    }

    function transferFrom(address from, address to, uint256 tokenId) public override onlyOwner {
		super.transferFrom(from, to, tokenId);
	}

	function safeTransferFrom(address from, address to, uint256 tokenId) public override onlyOwner {
		super.safeTransferFrom(from, to, tokenId);
	}

	function safeTransferFrom(address from, address to, uint256 tokenId, bytes memory _data) public override onlyOwner {
		super.safeTransferFrom(from, to, tokenId, _data);
	}


    function _beforeTokenTransfer(
        address sender,
        address recipient,
        uint256 tokenId
    ) internal override {
        // require(
        //     recipient == address(0) || balanceOf(recipient) == 0,
        //     "recipient is already invited."
        // );
        // require(
        //     recipient == address(0) || _vouches[recipient] >= _minimumVouches,
        //     "recipient didn't receive minimum vouches."
        // );
        // _invites[sender] = 0;
        // _invites[recipient] = tokenId;
        // if (recipient == address(0)) {
        //     Counters.increment(_inviteBurned);
        // }
    }
}
