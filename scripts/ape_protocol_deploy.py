from brownie import accounts, Wei, chain, ApeRegistryBeacon, ApeVaultWrapperImplementation, ApeVaultFactoryBeacon, ApeDistributor, ApeRegistry, ApeRouter, FeeRegistry, MockRegistry, MockVaultFactory, MockToken, MockVault
import json


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

def deploy_fresh_protocol_testnet():
	user = accounts.from_mnemonic('shoe please gift enter social raccoon badge bitter evolve thunder wing joke')

	multi_sig = accounts.from_mnemonic('absurd napkin barrel goose actual beauty volume dish carpet spoon forest scrap', count=1)
	lock_length = 60 * 60 * 24 * 14 # 14 days

	# mock_yearn_reg = MockRegistry.deploy({'from':user}, publish_source=False)
	# mock_yearn_vault_factories = MockVaultFactory.deploy(mock_yearn_reg, {'from':user}, publish_source=False)
	mock_ape_reg = ApeRegistry.deploy(multi_sig, 0, {'from':user}, publish_source=False)
	mock_vault_imp = ApeVaultWrapperImplementation.deploy({'from':user}, publish_source=False)
	mock_registry_beacon = ApeRegistryBeacon.deploy(mock_vault_imp, 0,{'from':user}, publish_source=False)
	mock_yearn_reg = MockRegistry.at('0xa64014AdF0E28a4c3f464e1Ebfccc0edAee0E559')
	mock_yearn_vault_factories = MockVaultFactory.at('0x5066CF36107E1f9B64A860dBEef3A1ba9E68a971')
	mock_ape_factory = ApeVaultFactoryBeacon.deploy(mock_yearn_reg, mock_ape_reg, mock_registry_beacon, {'from':user}, publish_source=False)
	mock_ape_router = ApeRouter.deploy(mock_yearn_reg, mock_ape_factory, 0, {'from':user}, publish_source=False)
	mock_ape_distro = ApeDistributor.deploy(mock_ape_reg, {'from':user}, publish_source=False)
	mock_ape_fee = FeeRegistry.deploy({'from':user}, publish_source=False)
	setup_protocol(mock_ape_reg, mock_ape_fee, mock_ape_distro, mock_ape_router, mock_ape_factory, user)
    # setup_mockvaults(mock_yearn_vault_factories, user)
	min_delay_call = mock_ape_reg.changeMinDelay.encode_input(lock_length)
	mock_ape_reg.schedule(mock_ape_reg, min_delay_call, '', '', 0, {'from':user})
	mock_ape_fee.schedule(mock_ape_fee, min_delay_call, '', '', 0, {'from':user})
	mock_ape_router.schedule(mock_ape_router, min_delay_call, '', '', 0, {'from':user})
	mock_ape_reg.execute(mock_ape_reg, min_delay_call, '', '', 0, {'from':user})
	mock_ape_fee.execute(mock_ape_fee, min_delay_call, '', '', 0, {'from':user})
	mock_ape_router.execute(mock_ape_router, min_delay_call, '', '', 0, {'from':user})
	mock_ape_reg.transferOwnership(multi_sig, {'from':user})
	mock_ape_fee.transferOwnership(multi_sig, {'from':user})
	mock_ape_router.transferOwnership(multi_sig, {'from':user})
	base_uri = 'https://goerli.etherscan.io/address/'
	print(f'Mock yearn reg: {base_uri + mock_yearn_reg.address}')
	print(f'Mock yearn Vault factory: {base_uri + mock_yearn_vault_factories.address}')
	print(f'Mock ape reg: {base_uri + mock_ape_reg.address}')
	print(f'Mock ape factory: {base_uri + mock_ape_factory.address}')
	print(f'Mock ape router: {base_uri + mock_ape_router.address}')
	print(f'Mock ape distro: {base_uri + mock_ape_distro.address}')
	print(f'Mock ape fee: {base_uri + mock_ape_fee.address}')
	testnet_deployInfo = {
	"ApeDistributor": {"address": mock_ape_distro.address},
	"ApeRegistry": {"address": mock_ape_reg.address},
	"ApeRegistryBeacon": {"address": mock_registry_beacon.address},
	"ApeRouter": {"address": mock_ape_router.address},
	"ApeVaultFactoryBeacon": {"address": mock_ape_factory.address},
	"ApeVaultWrapperImplementation": {"address": mock_vault_imp.address},
	"FeeRegistry": {"address": mock_ape_fee.address},
	"MockRegistry": {"address": mock_yearn_reg.address},
	"MockVaultFactory": {"address": mock_yearn_vault_factories.address}
}
	print(json.dumps(testnet_deployInfo, indent=2))

def deploy_protocol_testnet():
	user = accounts.load('moist', '\0')
	# user = accounts[0]

	multi_sig = accounts.from_mnemonic('absurd napkin barrel goose actual beauty volume dish carpet spoon forest scrap', count=1)
	lock_length = 60 * 60 * 24 * 14 # 14 days

	# mock_yearn_reg = MockRegistry.deploy({'from':user}, publish_source=True)
	# mock_yearn_vault_factories = MockVaultFactory.deploy(mock_yearn_reg, {'from':user}, publish_source=True)
	# mock_ape_reg = ApeRegistry.deploy(multi_sig, 0, {'from':user}, publish_source=True)
	# mock_vault_imp = ApeVaultWrapperImplementation.deploy({'from':user}, publish_source=True)
	# mock_registry_beacon = ApeRegistryBeacon.deploy(mock_vault_imp, 0,{'from':user}, publish_source=True)
	mock_yearn_reg = MockRegistry.at('0xe8a0721aF820630398994127C5592d41bB939689')
	mock_yearn_vault_factories = MockVaultFactory.at('0xf968AF55F713BA8284f24c37de8636529b3F9425')
	mock_ape_reg = ApeRegistry.at('0xF2bbE9Ac416F94B68741458930648527EA91657F')
	mock_vault_imp = ApeVaultWrapperImplementation.at('0x8960C6e08f3b87Bf84D602f322A88356Db458e18')
	mock_registry_beacon = ApeRegistryBeacon.at('0x2223C43cBb211133B5Cb7d964a5fD6709072F6c1')
	# mock_ape_factory = ApeVaultFactoryBeacon.deploy(mock_yearn_reg, mock_ape_reg, mock_registry_beacon, {'from':user}, publish_source=True)
	# mock_ape_router = ApeRouter.deploy(mock_yearn_reg, mock_ape_factory, 0, {'from':user}, publish_source=True)
	# mock_ape_distro = ApeDistributor.deploy(mock_ape_reg, {'from':user}, publish_source=True)
	# mock_ape_fee = FeeRegistry.deploy({'from':user}, publish_source=True)
	mock_ape_factory = ApeVaultFactoryBeacon.at('0x3050DC26CC0d2DB8085f049910a5D45EaF89c645')
	mock_ape_router = ApeRouter.at('0x074941E4E4ba9EBdDe284aF325ed23B75690191B')
	mock_ape_distro = ApeDistributor.at('0x6Abc75Fb66e5289D306dE428Cf5f6a3a15cE7e98')
	mock_ape_fee = FeeRegistry.at('0x81f3A59B9e262e27B9c7717e7002d82c2bccDa27')
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
