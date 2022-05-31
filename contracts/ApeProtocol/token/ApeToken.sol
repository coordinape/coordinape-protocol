// SPDX-License-Identifier: AGPL-3.0-only
pragma solidity ^0.8.2;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
import "./TokenAccessControl.sol";

contract COToken is ERC20("coordinape.com", "CO"), TokenAccessControl {
	uint256 immutable private _cap = 1_000_000_000 ether;

	bytes32 private immutable _PERMIT_TYPEHASH = keccak256("Permit(address owner,address spender,uint256 value,uint256 nonce,uint256 deadline)");

	mapping(address => uint256) public nonces;

	constructor() {
	}

	function cap() public view virtual returns (uint256) {
        return _cap;
    }

	function _mint(address account, uint256 amount) internal virtual override {
        require(totalSupply() + amount <= cap(), "COToken: cap exceeded");
        super._mint(account, amount);
    }

    function mint(address _account, uint256 _amount) external isMinter(msg.sender) {
        _mint(_account, _amount);
    }

    function DOMAIN_SEPARATOR() public view returns(bytes32) {
        uint chainId = block.chainid;
        return keccak256(
            abi.encode(
                keccak256('EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)'),
                keccak256(bytes("coordinape.com")),
                keccak256(bytes('1')),
                chainId,
                address(this)
            )
        );
    }

	function permit(address owner, address spender, uint256 value, uint256 deadline, uint8 v, bytes32 r, bytes32 s) public {
        require(block.timestamp <= deadline, "COToken: expired deadline");
        require(owner != address(0), "COToken: owner can't be ZERO address ");

        bytes32 digest = keccak256(
            abi.encode(
				'\x19\x01',
                DOMAIN_SEPARATOR(),
                keccak256(abi.encode(_PERMIT_TYPEHASH, owner, spender, value, nonces[owner]++, deadline))
            )
        );

        address signer = ECDSA.recover(digest, v, r, s);
        require(signer == owner, "COToken: invalid signature");

        _approve(owner, spender, value);
    }

    function transfer(address _to, uint256 _amount) public override notPaused returns(bool) {
        require(_to != address(this), "COToken: Cannot transfer to self");
        return ERC20.transfer(_to, _amount);
    }

    function transferFrom(address _from, address _to, uint256 _amount) public override notPaused returns(bool) {
        require(_to != address(this), "COToken: Cannot transfer to self");
        return ERC20.transferFrom(_from, _to, _amount);
    }
}