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

def test_migration(mock_ape_reg, mock_ape_fee, mock_ape_distro, mock_ape_router_beacon, mock_ape_factory_beacon, mock_yearn_vault_factories, ApeVaultWrapperImplementation, MockVault, minter, MockToken, mock_yearn_reg, interface):
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


    another_vault_tx = mock_yearn_vault_factories.createVault(mock_token, 'yvhello2', 'yvh2', {'from':user})
    v2_vault = MockVault.at(another_vault_tx.new_contracts[0])
    assert mock_yearn_reg.latestVault(mock_token) == v2_vault
    assert mock_yearn_reg.numVaults(mock_token) == 2
    ape_vault.apeMigrate({'from':user})
    assert ape_vault.vault() == v2_vault
    assert v2_vault.totalSupply() == amount
    assert mock_token.balanceOf(v2_vault) == amount
