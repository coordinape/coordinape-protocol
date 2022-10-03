from brownie import accounts, Wei, chain, VaultBeacon, ApeVaultWrapperImplementation, ApeVaultFactory, ApeDistributor, ApeRegistry, ApeRouter, FeeRegistry, MockRegistry, MockVaultFactory, MockToken, MockVault


def deploy_token():
	funds = accounts.load('moist', '\0')
	user = accounts.load('ape_deployer', '\0')
	multi_sig = '0x15B513F658f7390D8720dCE321f50974B28672EF'

	# funds.transfer(to=user, amount='1 ether')
	# ape = ApeToken.deploy({'from':user}, publish_source=True)
	# ape.transferOwnership(multi_sig, {'from':user})
	gas_used = Wei('150 gwei') * 21000
	remaining = user.balance() - gas_used
	ask_back = Wei('1 ether') - remaining
	print(f'to ask back: {Wei(ask_back).to("ether")}')
	user.transfer(to=funds, amount=remaining, gas_price='150 gwei')

def deploy_protocol():
	user = accounts.load('ape_deployer', '\0')

	multi_sig = ''
	lock_length = 60 * 60 * 24 * 14 # 14 days

	yearn_reg = '0x50c1a2ea0a861a967d9d0ffe2ae4012c2e053804'
	ape_reg = ApeRegistry.deploy(0, {'from':user}, publish_source=True)
	ape_factory = ApeVaultFactory.deploy(yearn_reg, ape_reg, {'from':user}, publish_source=True)
	ape_router = ApeRouter.deploy(yearn_reg, ape_factory, 0, {'from':user}, publish_source=True)
	ape_distro = ApeDistributor.deploy({'from':user}, publish_source=True)
	ape_fee = FeeRegistry.deploy({'from':user}, publish_source=True)
	setup_protocol(ape_reg, ape_fee, ape_distro, ape_router, ape_factory, user)
	min_delay_call = ape_reg.changeMinDelay.encode_input(lock_length)
	ape_reg.schedule(ape_reg, min_delay_call, '', '', 0, {'from':user})
	ape_fee.schedule(ape_fee, min_delay_call, '', '', 0, {'from':user})
	ape_router.schedule(ape_router, min_delay_call, '', '', 0, {'from':user})
	ape_reg.execute(ape_reg, min_delay_call, '', '', 0, {'from':user})
	ape_fee.execute(ape_fee, min_delay_call, '', '', 0, {'from':user})
	ape_router.execute(ape_router, min_delay_call, '', '', 0, {'from':user})
	ape_reg.transferOwnership(multi_sig, {'from':user})
	ape_fee.transferOwnership(multi_sig, {'from':user})
	ape_router.transferOwnership(multi_sig, {'from':user})
	

def deploy_protocol_testnet():
	user = accounts.load('moist', '\0')
	# user = accounts[0]
	
	multi_sig = accounts.from_mnemonic('absurd napkin barrel goose actual beauty volume dish carpet spoon forest scrap', count=1)
	lock_length = 60 * 60 * 24 * 14 # 14 days

	# mock_yearn_reg = MockRegistry.deploy({'from':user}, publish_source=True)
	# mock_yearn_vault_factories = MockVaultFactory.deploy(mock_yearn_reg, {'from':user}, publish_source=True)
	# mock_ape_reg = ApeRegistry.deploy(multi_sig, 0, {'from':user}, publish_source=True)
	# mock_vault_imp = ApeVaultWrapperImplementation.deploy({'from':user}, publish_source=True)
	# mock_registry_beacon = VaultBeacon.deploy(mock_vault_imp, 0,{'from':user}, publish_source=True)
	mock_yearn_reg = MockRegistry.at('0xe8a0721aF820630398994127C5592d41bB939689')
	mock_yearn_vault_factories = MockVaultFactory.at('0xf968AF55F713BA8284f24c37de8636529b3F9425')
	mock_ape_reg = ApeRegistry.at('0x679FE7F8D263B738953151affF97F3af51E0A126')
	mock_vault_imp = ApeVaultWrapperImplementation.at('0xB4F0834b552c473A39EE6Ae7058E6735d95F856D')
	mock_registry_beacon = VaultBeacon.at('0xC1AB48d19B63d0330f71d423bEEacdB2104D3DaF')
	# mock_ape_factory = ApeVaultFactory.deploy(mock_yearn_reg, mock_ape_reg, mock_registry_beacon, {'from':user}, publish_source=True)
	# mock_ape_router = ApeRouter.deploy(mock_yearn_reg, mock_ape_factory, 0, {'from':user}, publish_source=True)
	# mock_ape_distro = ApeDistributor.deploy(mock_ape_reg, {'from':user}, publish_source=True)
	# mock_ape_fee = FeeRegistry.deploy({'from':user}, publish_source=True)
	mock_ape_factory = ApeVaultFactory.at('0x38034CCECa1A6ce2Bc1cA736D4134AF994154660')
	mock_ape_router = ApeRouter.at('0x04Ad1e2Af8A4331a6a10D4b7Ae92e983bD5b33C2')
	mock_ape_distro = ApeDistributor.at('0x1C07320B1588885d3cddacb3e592622dbf9e28e6')
	mock_ape_fee = FeeRegistry.at('0x5Bd2C39d5CB3344601b2ACF0C36eEf28Bac18068')
	# setup_protocol(mock_ape_reg, mock_ape_fee, mock_ape_distro, mock_ape_router, mock_ape_factory, user)
	setup_mockvaults(mock_yearn_vault_factories, user)
	# min_delay_call = mock_ape_reg.changeMinDelay.encode_input(lock_length)
	# mock_ape_reg.schedule(mock_ape_reg, min_delay_call, '', '', 0, {'from':user})
	# mock_ape_fee.schedule(mock_ape_fee, min_delay_call, '', '', 0, {'from':user})
	# mock_ape_router.schedule(mock_ape_router, min_delay_call, '', '', 0, {'from':user})
	# mock_ape_reg.execute(mock_ape_reg, min_delay_call, '', '', 0, {'from':user})
	# mock_ape_fee.execute(mock_ape_fee, min_delay_call, '', '', 0, {'from':user})
	# mock_ape_router.execute(mock_ape_router, min_delay_call, '', '', 0, {'from':user})
	# mock_ape_reg.transferOwnership(multi_sig, {'from':user})
	# mock_ape_fee.transferOwnership(multi_sig, {'from':user})
	# mock_ape_router.transferOwnership(multi_sig, {'from':user})
	base_uri = 'https://goerli.etherscan.io/address/'
	print(f'Mock yearn reg: {base_uri + mock_yearn_reg.address}')
	print(f'Mock yearn Vault factory: {base_uri + mock_yearn_vault_factories.address}')
	print(f'Mock ape reg: {base_uri + mock_ape_reg.address}')
	print(f'Mock ape factory: {base_uri + mock_ape_factory.address}')
	print(f'Mock ape router: {base_uri + mock_ape_router.address}')
	print(f'Mock ape distro: {base_uri + mock_ape_distro.address}')
	print(f'Mock ape fee: {base_uri + mock_ape_fee.address}')



def setup_protocol(ape_reg, ape_fee, ape_distro, ape_router, ape_factory, minter):
    set_fee_call = ape_reg.setFeeRegistry.encode_input(ape_fee)
    set_router_call = ape_reg.setRouter.encode_input(ape_router)
    set_distro_call = ape_reg.setDistributor.encode_input(ape_distro)
    set_factory_call = ape_reg.setFactory.encode_input(ape_factory)
    set_treasury_call = ape_reg.setTreasury.encode_input(minter)
    ape_reg.schedule(ape_reg, set_fee_call, '', '', 0, {'from':minter})
    ape_reg.schedule(ape_reg, set_router_call, '', '', 0, {'from':minter})
    ape_reg.schedule(ape_reg, set_distro_call, '', '', 0, {'from':minter})
    ape_reg.schedule(ape_reg, set_factory_call, '', '', 0, {'from':minter})
    ape_reg.schedule(ape_reg, set_treasury_call, '', '', 0, {'from':minter})
    ape_reg.execute(ape_reg, set_fee_call, '', '', 0, {'from':minter})
    ape_reg.execute(ape_reg, set_router_call, '', '', 0, {'from':minter})
    ape_reg.execute(ape_reg, set_distro_call, '', '', 0, {'from':minter})
    ape_reg.execute(ape_reg, set_factory_call, '', '', 0, {'from':minter})
    ape_reg.execute(ape_reg, set_treasury_call, '', '', 0, {'from':minter})

def setup_mockvaults(mock_yearn_vault_factories, user):
# 	usdc = MockToken.deploy('USD Coin', 'USDC', {'from':user}, publish_source=True)
# 	dai = MockToken.deploy('Dai', 'DAI', {'from':user})
# 	ape = MockToken.deploy('Ape', 'OOH', {'from':user})
	usdc = MockToken.at('0x0e96493B9011e733ef8E4255092626705E462b8e')
	dai = MockToken.at('0x8e34054aA3F9CD541fE4B0fb9c4A45281178e7c6')
	ape = MockToken.at('0x65AE42B1c82BF9E2A270B2cf26D1fb28639e8793')
	# tx1 = mock_yearn_vault_factories.createVault(usdc, 'yearnVault USDC', 'yvUSDC', {'from':user})
	# # MockVault.publish_source(tx1.new_contracts[0])
	# tx2 = mock_yearn_vault_factories.createVault(dai, 'yearnVault DAI', 'yvDAI', {'from':user})
	# tx3 = mock_yearn_vault_factories.createVault(ape, 'yearnVault Ape', 'yvOOH', {'from':user})

	base_uri = 'https://goerli.etherscan.io/address/'
	print(f'Mock usdc: {base_uri + usdc.address}')
	print(f'Mock dai: {base_uri + dai.address}')
	print(f'Mock ape token: {base_uri + ape.address}')
	print(f'Mock usdc vault: {base_uri + "0xd0374e274619dc3cf7d13de76104f1f0c73c9d64"}')
	print(f'Mock dai vault: {base_uri + "0x299d08da3afa3af6d60257e9cea1b20d228d58c8"}')
	print(f'Mock ape vault: {base_uri + "0x10dd830cc919ce763315692f135fe332355d7ab5"}')
