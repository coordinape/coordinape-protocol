from brownie import accounts, chain, reverts, Wei
import json

TAP_BASE = 1
TAP_PROFIT = 0

def setup_protocol(mock_ape_reg, mock_ape_fee, mock_ape_distro, mock_ape_router_beacon, mock_ape_factory_beacon, minter):
    set_fee_call = mock_ape_reg.setFeeRegistry.encode_input(mock_ape_fee)
    set_router_call = mock_ape_reg.setRouter.encode_input(mock_ape_router_beacon)
    set_distro_call = mock_ape_reg.setDistributor.encode_input(mock_ape_distro)
    set_factory_call = mock_ape_reg.setFactory.encode_input(mock_ape_factory_beacon)
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

def test_tap_profit(mock_ape_reg, mock_ape_fee, mock_ape_distro, mock_ape_router_beacon, mock_ape_factory_beacon, mock_yearn_vault_factories, ApeVaultWrapperImplementation, MockVault, minter, MockToken, interface):
    setup_protocol(mock_ape_reg, mock_ape_fee, mock_ape_distro, mock_ape_router_beacon, mock_ape_factory_beacon, minter)
    user = accounts[0]
    amount = 1_000_000_000_000
    #          100_000_000_000
    mock_token = MockToken.deploy('hello', 'h',{'from':user})
    mock_token.mint(amount, {'from':user})
    mock_token.approve(mock_ape_router_beacon, 2 ** 256 -1, {'from':user})
    new_vault_tx = mock_yearn_vault_factories.createVault(mock_token, 'yvhello', 'yvh',{'from':user})
    vault = MockVault.at(new_vault_tx.new_contracts[0])
    tx = mock_ape_factory_beacon.createApeVault(mock_token, '0x0000000000000000000000000000000000000000', {'from':user})
    ape_vault = ApeVaultWrapperImplementation.at(tx.new_contracts[0])
    mock_ape_router_beacon.delegateDeposit(ape_vault, mock_token, amount, {'from':user})
    assert vault.balanceOf(ape_vault) >= amount

    # 10% yield
    vault.goodHarvest(10, {'from':user})
    
    circle = '0x1'
    token = vault
    grant = amount
    interval = 60 * 60 * 14 # 14 days
    epochs = 0
    root = '0x1838e0c6251730868cce6768e2062af0e72f79409a1f7011351bd2c1535e2a5c'
    ape_vault.updateAllowance(circle, token, grant, interval, epochs, 0,{'from':user})
    admin = accounts[1]
    ape_vault.updateCircleAdmin(circle, admin, {'from':user})
    with reverts('Not enough profit to cover epoch'):
        mock_ape_distro.uploadEpochRoot(ape_vault, circle, token, root, grant, TAP_PROFIT, {'from': admin})
    share_total = vault.balanceOf(ape_vault)
    #  not 1/11 as we have fee added now
    mock_ape_distro.uploadEpochRoot(ape_vault, circle, token, root, share_total // 12, TAP_PROFIT, {'from': admin})
    assert vault.balanceOf(mock_ape_distro) >= (share_total // 12) * 99 // 100

def test_expected_profit_revert(mock_ape_reg, mock_ape_fee, mock_ape_distro, mock_ape_router_beacon, mock_ape_factory_beacon, mock_yearn_vault_factories, ApeVaultWrapperImplementation, MockVault, minter, MockToken, interface):
    setup_protocol(mock_ape_reg, mock_ape_fee, mock_ape_distro, mock_ape_router_beacon, mock_ape_factory_beacon, minter)
    user = accounts[0]
    amount = 1_000_000_000_000
    #          100_000_000_000
    mock_token = MockToken.deploy('hello', 'h',{'from':user})
    mock_token.mint(amount, {'from':user})
    mock_token.approve(mock_ape_router_beacon, 2 ** 256 -1, {'from':user})
    new_vault_tx = mock_yearn_vault_factories.createVault(mock_token, 'yvhello', 'yvh',{'from':user})
    vault = MockVault.at(new_vault_tx.new_contracts[0])
    tx = mock_ape_factory_beacon.createApeVault(mock_token, '0x0000000000000000000000000000000000000000', {'from':user})
    ape_vault = ApeVaultWrapperImplementation.at(tx.new_contracts[0])
    mock_ape_router_beacon.delegateDeposit(ape_vault, mock_token, amount, {'from':user})
    assert vault.balanceOf(ape_vault) >= amount

    # 10% yield
    vault.badHarvest(10, {'from':user})
    
    circle = '0x1'
    token = vault
    grant = amount
    interval = 60 * 60 * 14 # 14 days
    epochs = 0
    root = '0x1838e0c6251730868cce6768e2062af0e72f79409a1f7011351bd2c1535e2a5c'
    ape_vault.updateAllowance(circle, token, grant, interval, epochs, 0,{'from':user})
    admin = accounts[1]
    ape_vault.updateCircleAdmin(circle, admin, {'from':user})
    with reverts('Not enough profit to cover epoch'):
        mock_ape_distro.uploadEpochRoot(ape_vault, circle, token, root, grant // 100, TAP_PROFIT, {'from': admin})
    print(vault.pricePerShare())
    print(ape_vault.profit())

def test_bad_harvest_reset_value(mock_ape_reg, mock_ape_fee, mock_ape_distro, mock_ape_router_beacon, mock_ape_factory_beacon, mock_yearn_vault_factories, ApeVaultWrapperImplementation, MockVault, minter, MockToken, interface):
    setup_protocol(mock_ape_reg, mock_ape_fee, mock_ape_distro, mock_ape_router_beacon, mock_ape_factory_beacon, minter)
    user = accounts[0]
    amount = 1_000_000_000_000
    #           20_000_000_000
    mock_token = MockToken.deploy('hello', 'h', {'from':user})
    mock_token.mint(amount, {'from':user})
    mock_token.approve(mock_ape_router_beacon, 2 ** 256 -1, {'from':user})
    new_vault_tx = mock_yearn_vault_factories.createVault(mock_token, 'yvhello', 'yvh',{'from':user})
    vault = MockVault.at(new_vault_tx.new_contracts[0])
    tx = mock_ape_factory_beacon.createApeVault(mock_token, '0x0000000000000000000000000000000000000000', {'from':user})
    ape_vault = ApeVaultWrapperImplementation.at(tx.new_contracts[0])
    mock_ape_router_beacon.delegateDeposit(ape_vault, mock_token, amount, {'from':user})
    assert vault.balanceOf(ape_vault) == amount

    # 90% bad yield
    vault.badHarvest(90, {'from':user})

    ape_vault.syncUnderlying({'from':user})
    print(f'underlying: {ape_vault.underlyingValue()}')
    
    circle = '0x1'
    token = vault
    grant = amount
    interval = 60 * 60 * 14 # 14 days
    epochs = 1
    root = '0x1838e0c6251730868cce6768e2062af0e72f79409a1f7011351bd2c1535e2a5c'
    ape_vault.updateAllowance(circle, token, grant, interval, epochs, 0,{'from':user})
    admin = accounts[1]
    ape_vault.updateCircleAdmin(circle, admin, {'from':user})
    with reverts('Not enough profit to cover epoch'):
        mock_ape_distro.uploadEpochRoot(ape_vault, circle, token, root, grant // 10, TAP_PROFIT, {'from': admin})
    vault.goodHarvest(100, {'from':user})
    mock_ape_distro.uploadEpochRoot(ape_vault, circle, token, root, grant // 10, TAP_BASE, {'from': admin})

    print(vault.pricePerShare())
    print(ape_vault.profit())