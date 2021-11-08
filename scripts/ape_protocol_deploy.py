from brownie import accounts, chain, ApeVaultWrapper, ApeVaultFactory, ApeDistributor, ApeRegistry, ApeRouter, FeeRegistry, MockRegistry, MockVaultFactory, MockToken

def deploy_protocol_testnet():
	user = accounts.load('moist', '\0')

	mock_yearn_reg = MockRegistry.deploy({'from':user})
	mock_yearn_vault_factories = MockVaultFactory.deploy(mock_yearn_reg, {'from':user})
	mock_ape_reg = ApeRegistry.deploy(0, {'from':user})
	mock_ape_factory = ApeVaultFactory.deploy(mock_yearn_reg, mock_ape_reg, {'from':user})
	mock_ape_router = ApeRouter.deploy(mock_yearn_reg, mock_ape_factory, 0, {'from':user})
	mock_ape_distro = ApeDistributor.deploy({'from':user})
	mock_ape_fee = FeeRegistry.deploy({'from':user})
	setup_protocol(mock_ape_reg, mock_ape_fee, mock_ape_distro, mock_ape_router, mock_ape_factory, user)
	setup_mockvaults(mock_yearn_vault_factories, user)



def setup_protocol(mock_ape_reg, mock_ape_fee, mock_ape_distro, mock_ape_router, mock_ape_factory, minter):
    set_fee_call = mock_ape_reg.setFeeRegistry.encode_input(mock_ape_fee)
    set_router_call = mock_ape_reg.setRouter.encode_input(mock_ape_router)
    set_distro_call = mock_ape_reg.setDistributor.encode_input(mock_ape_distro)
    set_factory_call = mock_ape_reg.setFactory.encode_input(mock_ape_factory)
    set_treasury_call = mock_ape_reg.setTreasury.encode_input(minter)
    mock_ape_reg.schedule(mock_ape_reg, set_fee_call, '', '', 0, {'from':minter})
    mock_ape_reg.schedule(mock_ape_reg, set_router_call, '', '', 0, {'from':minter})
    mock_ape_reg.schedule(mock_ape_reg, set_distro_call, '', '', 0, {'from':minter})
    mock_ape_reg.schedule(mock_ape_reg, set_factory_call, '', '', 0, {'from':minter})
    mock_ape_reg.schedule(mock_ape_reg, set_treasury_call, '', '', 0, {'from':minter})
    mock_ape_reg.execute(mock_ape_reg, set_fee_call, '', '', 0, {'from':minter})
    mock_ape_reg.execute(mock_ape_reg, set_router_call, '', '', 0, {'from':minter})
    mock_ape_reg.execute(mock_ape_reg, set_distro_call, '', '', 0, {'from':minter})
    mock_ape_reg.execute(mock_ape_reg, set_factory_call, '', '', 0, {'from':minter})
    mock_ape_reg.execute(mock_ape_reg, set_treasury_call, '', '', 0, {'from':minter})

def setup_mockvaults(mock_yearn_vault_factories, user):
	usdc = MockToken.deploy('USD Coin', 'USDC', {'from':user})
	dai = MockToken.deploy('Dai', 'DAI', {'from':user})
	ape = MockToken.deploy('Ape', 'OOH', {'from':user})
	mock_yearn_vault_factories.createVault(usdc, 'yearnVault USDC', 'yvUSDC', {'from':user})
	mock_yearn_vault_factories.createVault(dai, 'yearnVault DAI', 'yvDAI', {'from':user})
	mock_yearn_vault_factories.createVault(ape, 'yearnVault Ape', 'yvOOH', {'from':user})