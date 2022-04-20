from brownie import accounts, Wei, chain, ApeRegistryBeacon, ApeVaultWrapperImplementation, ApeVaultFactoryBeacon, ApeDistributor, ApeRegistry, ApeRouter, FeeRegistry, MockRegistry, MockVaultFactory, MockToken, MockVault


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
	ape_factory = ApeVaultFactoryBeacon.deploy(yearn_reg, ape_reg, {'from':user}, publish_source=True)
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
	# user = accounts.load('moist', '\0')
	user = accounts[0]
	
	multi_sig = user
	lock_length = 60 * 60 * 24 * 14 # 14 days

	mock_yearn_reg = MockRegistry.deploy({'from':user}, publish_source=False)
	mock_yearn_vault_factories = MockVaultFactory.deploy(mock_yearn_reg, {'from':user}, publish_source=False)
	mock_ape_reg = ApeRegistry.deploy(multi_sig, 0, {'from':user}, publish_source=False)
	mock_vault_imp = ApeVaultWrapperImplementation.deploy({'from':user}, publish_source=False)
	mock_registry_beacon = ApeRegistryBeacon.deploy(mock_vault_imp, 0,{'from':user}, publish_source=False)
	mock_ape_factory = ApeVaultFactoryBeacon.deploy(mock_yearn_reg, mock_ape_reg, mock_registry_beacon, {'from':user}, publish_source=False)
	mock_ape_router = ApeRouter.deploy(mock_yearn_reg, mock_ape_factory, 0, {'from':user}, publish_source=False)
	mock_ape_distro = ApeDistributor.deploy(mock_ape_reg, {'from':user}, publish_source=False)
	mock_ape_fee = FeeRegistry.deploy({'from':user}, publish_source=False)
	setup_protocol(mock_ape_reg, mock_ape_fee, mock_ape_distro, mock_ape_router, mock_ape_factory, user)
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
	usdc = MockToken.deploy('USD Coin', 'USDC', {'from':user}, publish_source=False)
	dai = MockToken.deploy('Dai', 'DAI', {'from':user})
	ape = MockToken.deploy('Ape', 'OOH', {'from':user})
	tx1 = mock_yearn_vault_factories.createVault(usdc, 'yearnVault USDC', 'yvUSDC', {'from':user})
	# MockVault.publish_source(tx1.new_contracts[0])
	tx2 = mock_yearn_vault_factories.createVault(dai, 'yearnVault DAI', 'yvDAI', {'from':user})
	tx3 = mock_yearn_vault_factories.createVault(ape, 'yearnVault Ape', 'yvOOH', {'from':user})

	base_uri = 'https://goerli.etherscan.io/address/'
	print(f'Mock usdc: {base_uri + usdc.address}')
	print(f'Mock dai: {base_uri + dai.address}')
	print(f'Mock ape token: {base_uri + ape.address}')
	print(f'Mock usdc vault: {base_uri + tx1.new_contracts[0]}')
	print(f'Mock dai vault: {base_uri + tx2.new_contracts[0]}')
	print(f'Mock ape vault: {base_uri + tx3.new_contracts[0]}')
