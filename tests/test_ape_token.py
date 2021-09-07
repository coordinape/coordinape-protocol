from brownie import accounts, chain, reverts, Wei


def test_pausing(accounts, ApeToken):
	ape = ApeToken.deploy({'from':accounts[0]})
	assert ape.balanceOf(accounts[0]) == Wei('200_000_000 ether')

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
	assert ape.balanceOf(accounts[0]) == Wei('200_000_000 ether')

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

# def generate_permit(account):
# 	pk = account.private_key
# 	permit_type_hash = web3.keccak(text='Permit(address owner,address spender,uint256 value,uint256 nonce,uint256 deadline)')
# 	base_message = web3.soliditySha3(
# 		[]
# 	)
# 	for row in rows:
#         _id = int(row[0])
#         genes = int(row[3])
#         base_message = web3.soliditySha3(
#             [ 'uint256' , 'uint256' ] , 
#             [_id, genes])
#         message = encode_defunct(base_message)
#         # signer's pk
#         sig = web3.eth.account.sign_message(message, '0x1111111111111111111111111111111111111111111111119d9d8371d8675d91')
#         data.append([row[0], row[1], row[2],row[3], web3.toHex(sig.signature)])
#     strcsv = ''
#     for row in data:
#         for i in range(len(row)):
#             strcsv += str(row[i])
#             if i != len(row) - 1:
#                 strcsv += ','
#         strcsv += '\n'