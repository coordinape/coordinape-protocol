from brownie import accounts, chain, reverts, Wei
from eth_account.messages import encode_defunct, encode_intended_validator, SignableMessage
from eth_abi import encode_single
import web3
import time

def test_pausing(accounts, ApeToken):
	ape = ApeToken.deploy({'from':accounts[0]})
	# Fund some APE tokens
	ape.addMinters([accounts[1].address], {'from':accounts[0]})
	ape.mint(accounts[0], '20 ether', {'from':accounts[1]})

	ape.transfer(accounts[1], Wei('1 ether'), {'from':accounts[0]})
	with reverts('Ownable: caller is not the owner'):
		ape.changePauseStatus(True, {'from':accounts[1]})
	ape.changePauseStatus(True, {'from':accounts[0]})
	with reverts('AccessControl: Contract is paused'):
		ape.transfer(accounts[1], Wei('1 ether'), {'from':accounts[0]})
	ape.changePauseStatus(False, {'from':accounts[0]})
	ape.transfer(accounts[1], Wei('1 ether'), {'from':accounts[0]})
	ape.disablePausingForever({'from':accounts[0]})
	ape.transfer(accounts[1], Wei('1 ether'), {'from':accounts[0]})
	with reverts('AccessControl: Contract is unpaused forever'):
		ape.changePauseStatus(False, {'from':accounts[0]})

def test_minting(accounts, ApeToken):
	ape = ApeToken.deploy({'from':accounts[0]})

	with reverts('AccessControl: Cannot mint'):
		ape.mint(accounts[4], '20 ether', {'from':accounts[1]})
	with reverts('Ownable: caller is not the owner'):
		ape.addMinters([add.address for add in accounts[1:3]], {'from':accounts[1]})
	ape.addMinters([add.address for add in accounts[1:3]], {'from':accounts[0]})
	ape.mint(accounts[4], '20 ether', {'from':accounts[1]})
	with reverts('ApeToken: cap exceeded'):
		ape.mint(accounts[4], '2_000_000_000 ether', {'from':accounts[1]})
	ape.mint(accounts[4], '799_999_960 ether', {'from':accounts[1]})
	ape.mint(accounts[4], '10 ether', {'from':accounts[2]})
	with reverts('Ownable: caller is not the owner'):
		ape.removeMinters([add.address for add in accounts[1:3]], {'from':accounts[1]})
	ape.removeMinters([add.address for add in accounts[1:3]], {'from':accounts[0]})
	with reverts('AccessControl: Cannot mint'):
		ape.mint(accounts[4], '5 ether', {'from':accounts[1]})
	ape.addMinters([add.address for add in accounts[1:3]], {'from':accounts[0]})
	ape.disableMintingForever({'from':accounts[0]})
	with reverts('AccessControl: Contract cannot mint tokens anymore'):
		ape.mint(accounts[4], '1 ether', {'from':accounts[1]})
	with reverts('AccessControl: Contract cannot mint tokens anymore'):
		ape.mint(accounts[4], '1 ether', {'from':accounts[5]})

def test_permit(ApeToken, accounts, web3):
	sig_accounts = accounts.from_mnemonic('wink fish soap tattoo riot thumb original surface rough obscure innocent junior', count=10)
	accounts[0].transfer(to=sig_accounts[0], amount='10 ether')
	ape = ApeToken.deploy({'from':sig_accounts[0]})
	# Fund some APE tokens
	ape.addMinters([accounts[1].address], {'from':sig_accounts[0]})
	ape.mint(accounts[2], '20 ether', {'from':accounts[1]})

	_from = sig_accounts[0].address
	to = accounts[0].address
	amount = Wei('150000 ether')
	nonce = 0
	deadline = int(time.time()) + 3600
	sig = generate_permit(web3, sig_accounts[0], to, amount, nonce, deadline, ape.DOMAIN_SEPARATOR())
	ape.permit(_from, to, amount, deadline, sig.v, sig.r, sig.s, {'from':accounts[2]})
	with reverts("ApeToken: invalid signature"):
		ape.permit(_from, to, amount, deadline, sig.v, sig.r, sig.s, {'from':accounts[2]})

	deadline = 10
	nonce = 1
	sig = generate_permit(web3, sig_accounts[0], to, amount, nonce, deadline, ape.DOMAIN_SEPARATOR())
	with reverts("ApeToken: expired deadline"):
		ape.permit(_from, to, amount, deadline, sig.v, sig.r, sig.s, {'from':accounts[2]})

def generate_permit(web3, _from, to, amount, nonce, deadline, domain_separator):
	init = '\x19\x01'
	permit_type_hash = web3.keccak(text='Permit(address owner,address spender,uint256 value,uint256 nonce,uint256 deadline)')
	data_hash = web3.keccak(encode_single(
		'(bytes32,address,address,uint256,uint256,uint256)',
		[permit_type_hash, _from.address, to, amount, nonce, deadline]
	))
	digest = web3.keccak(encode_single('(string,bytes32,bytes32)', [init, domain_separator, data_hash]))

	sig = web3.eth.account.signHash(digest, _from.private_key)
	return sig