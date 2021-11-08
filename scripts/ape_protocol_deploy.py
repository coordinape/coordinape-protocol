from brownie import accounts, chain, ApeVaultWrapper, ApeVaultFactory, ApeDistributor, ApeRegistry, ApeRouter, FeeRegistry, MockRegistry, MockVaultFactory, MockToken

def deploy_protocol():
	user = accounts.load('moist', '\0')

	multi_sig = ''
	lock_length = 60 * 60 * 24 * 14 # 14 days

	yearn_reg = '0x50c1a2ea0a861a967d9d0ffe2ae4012c2e053804'
	ape_reg = ApeRegistry.deploy(0, {'from':user})
	ape_factory = ApeVaultFactory.deploy(yearn_reg, ape_reg, {'from':user})
	ape_router = ApeRouter.deploy(yearn_reg, ape_factory, 0, {'from':user})
	ape_distro = ApeDistributor.deploy({'from':user})
	ape_fee = FeeRegistry.deploy({'from':user})
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
	
	multi_sig = '0x50c1a2ea0a861a967d9d0ffe2ae4012c2e053804'
	lock_length = 60 * 60 * 24 * 14 # 14 days

	mock_yearn_reg = MockRegistry.deploy({'from':user})
	mock_yearn_vault_factories = MockVaultFactory.deploy(mock_yearn_reg, {'from':user})
	mock_ape_reg = ApeRegistry.deploy(0, {'from':user})
	mock_ape_factory = ApeVaultFactory.deploy(mock_yearn_reg, mock_ape_reg, {'from':user})
	mock_ape_router = ApeRouter.deploy(mock_yearn_reg, mock_ape_factory, 0, {'from':user})
	mock_ape_distro = ApeDistributor.deploy({'from':user})
	mock_ape_fee = FeeRegistry.deploy({'from':user})
	setup_protocol(mock_ape_reg, mock_ape_fee, mock_ape_distro, mock_ape_router, mock_ape_factory, user)
	setup_mockvaults(mock_yearn_vault_factories, user)
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
	usdc = MockToken.deploy('USD Coin', 'USDC', {'from':user})
	dai = MockToken.deploy('Dai', 'DAI', {'from':user})
	ape = MockToken.deploy('Ape', 'OOH', {'from':user})
	mock_yearn_vault_factories.createVault(usdc, 'yearnVault USDC', 'yvUSDC', {'from':user})
	mock_yearn_vault_factories.createVault(dai, 'yearnVault DAI', 'yvDAI', {'from':user})
	mock_yearn_vault_factories.createVault(ape, 'yearnVault Ape', 'yvOOH', {'from':user})