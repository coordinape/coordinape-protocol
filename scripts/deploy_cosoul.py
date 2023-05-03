from brownie import CoSoul, accounts, SoulProxy, Contract


def main():
	user = accounts.load('owl_eth', '\0')
	user1 = accounts.load('personal_dep', '\0')
	pub = True
	_imp = CoSoul.deploy({'from':user}, publish_source=pub)
	signer = accounts.from_mnemonic('blur buffalo client property frog destroy torch daughter excite obscure nasty patient')
	data = _imp.initialize.encode_input('CoSoul', '[Soul]', signer)
	proxy = SoulProxy.deploy(_imp.address, user1, data, {'from': user}, publish_source=pub)
