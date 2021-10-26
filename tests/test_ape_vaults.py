from brownie import accounts, chain, reverts, Wei
from eth_account.messages import encode_defunct, encode_intended_validator, SignableMessage
from eth_abi import encode_single
import web3

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

def test_vault_creation(ape_reg, ape_fee, ape_distro, ape_router, ape_factory, big_usdc, usdc, ApeVaultWrapper, minter):
    setup_protocol(ape_reg, ape_fee, ape_distro, ape_router, ape_factory, minter)
    user = accounts[0]
    tx = ape_factory.createApeVault(usdc, '0x0000000000000000000000000000000000000000', {'from':user})
    ape_vault = ApeVaultWrapper.at(tx.new_contracts[0])
    assert ape_vault.owner() == user
    assert ape_vault.token() == usdc
    usdc_vault = '0x5f18C75AbDAe578b483E5F43f12a39cF75b973a9'
    assert ape_vault.vault() == usdc_vault

def test_router(ape_reg, ape_fee, ape_distro, ape_router, ape_factory, big_usdc, usdc, ApeVaultWrapper, minter, interface):
    setup_protocol(ape_reg, ape_fee, ape_distro, ape_router, ape_factory, minter)
    user = accounts[0]
    amount = 1_000_000_000_000
    usdc.transfer(user, amount, {'from':big_usdc})
    usdc.approve(ape_router, 2 ** 256 -1, {'from':user})
    tx = ape_factory.createApeVault(usdc, '0x0000000000000000000000000000000000000000', {'from':user})
    ape_vault = ApeVaultWrapper.at(tx.new_contracts[0])
    assert ape_vault.owner() == user
    assert ape_vault.token() == usdc
    usdc_vault = interface.IERC20('0x5f18C75AbDAe578b483E5F43f12a39cF75b973a9')
    assert ape_vault.vault() == usdc_vault
    with reverts('ApeRouter: Vault does not exist'):
        ape_router.delegateDeposit(usdc, usdc, amount, {'from':user})
    with reverts(''):
        ape_router.delegateDeposit(ape_vault, usdc_vault, amount, {'from':user})
    with reverts('ApeRouter: yearn Vault not identical'):
        dai = '0x6b175474e89094c44da98b954eedeac495271d0f'
        ape_router.delegateDeposit(ape_vault, dai, amount, {'from':user})
    ape_router.delegateDeposit(ape_vault, usdc, amount, {'from':user})
    assert usdc_vault.balanceOf(ape_vault) > 0
    assert ape_vault.underlyingValue() == amount

def test_vault_exit(ape_reg, ape_fee, ape_distro, ape_router, ape_factory, big_usdc, usdc, ApeVaultWrapper, minter, interface):
    setup_protocol(ape_reg, ape_fee, ape_distro, ape_router, ape_factory, minter)
    user = accounts[0]
    amount = 1_000_000_000_000
    usdc.transfer(user, amount, {'from':big_usdc})
    usdc.approve(ape_router, 2 ** 256 -1, {'from':user})
    tx = ape_factory.createApeVault(usdc, '0x0000000000000000000000000000000000000000', {'from':user})
    ape_vault = ApeVaultWrapper.at(tx.new_contracts[0])
    usdc_vault = interface.IERC20('0x5f18C75AbDAe578b483E5F43f12a39cF75b973a9')
    ape_router.delegateDeposit(ape_vault, usdc, amount, {'from':user})
    yv_bal = usdc_vault.balanceOf(ape_vault)
    ape_vault.exitVaultToken(False, {'from':user})
    assert usdc_vault.balanceOf(user) == yv_bal

def test_vault_exit_underlying(ape_reg, ape_fee, ape_distro, ape_router, ape_factory, big_usdc, usdc, ApeVaultWrapper, minter, interface):
    setup_protocol(ape_reg, ape_fee, ape_distro, ape_router, ape_factory, minter)
    user = accounts[0]
    amount = 1_000_000_000_000
    usdc.transfer(user, amount, {'from':big_usdc})
    usdc.approve(ape_router, 2 ** 256 -1, {'from':user})
    tx = ape_factory.createApeVault(usdc, '0x0000000000000000000000000000000000000000', {'from':user})
    ape_vault = ApeVaultWrapper.at(tx.new_contracts[0])
    usdc_vault = interface.IERC20('0x5f18C75AbDAe578b483E5F43f12a39cF75b973a9')
    ape_router.delegateDeposit(ape_vault, usdc, amount, {'from':user})
    yv_bal = usdc_vault.balanceOf(ape_vault)
    ape_vault.exitVaultToken(True, {'from':user})
    assert usdc_vault.balanceOf(ape_vault) <= Wei('1_000_000 ether') // 1000
    assert usdc.balanceOf(user) > 0

def test_vault_withdraw_underlying(ape_reg, ape_fee, ape_distro, ape_router, ape_factory, big_usdc, usdc, ApeVaultWrapper, minter, interface):
    setup_protocol(ape_reg, ape_fee, ape_distro, ape_router, ape_factory, minter)
    user = accounts[0]
    amount = 1_000_000_000_000
    usdc.transfer(user, amount, {'from':big_usdc})
    usdc.approve(ape_router, 2 ** 256 -1, {'from':user})
    tx = ape_factory.createApeVault(usdc, '0x0000000000000000000000000000000000000000', {'from':user})
    ape_vault = ApeVaultWrapper.at(tx.new_contracts[0])
    usdc_vault = interface.IERC20('0x5f18C75AbDAe578b483E5F43f12a39cF75b973a9')
    ape_router.delegateDeposit(ape_vault, usdc, amount, {'from':user})
    yv_bal = usdc_vault.balanceOf(ape_vault)
    expected = 200_000_000_000
    ape_vault.apeWithdrawUnderlying(expected, {'from':user})
    assert usdc.balanceOf(user) >= expected * 99 // 100 

def test_migrate():
    pass

def test_circle_allowance(ape_reg, ape_fee, ape_distro, ape_router, ape_factory, big_usdc, usdc, ApeVaultWrapper, minter, interface):
    setup_protocol(ape_reg, ape_fee, ape_distro, ape_router, ape_factory, minter)
    user = accounts[0]
    circle = '0x1'
    token = usdc
    amount = 20_000_000_000
    interval = 60 * 60 * 14 # 14 days
    epochs = 4
    tx = ape_factory.createApeVault(usdc, '0x0000000000000000000000000000000000000000', {'from':user})
    ape_vault = ApeVaultWrapper.at(tx.new_contracts[0])
    ape_vault.updateAllowance(circle, usdc, 20_000_000_000, interval, epochs, {'from':user})
    (debt, intervalStart, epochs) = ape_distro.currentAllowances(ape_vault, circle, token)
    assert ape_distro.allowances(ape_vault, circle, token) == (amount, interval)
    assert debt == 0 and epochs == 4

def test_vault_circle_admin(ape_reg, ape_fee, ape_distro, ape_router, ape_factory, big_usdc, usdc, ApeVaultWrapper, minter, interface):
    setup_protocol(ape_reg, ape_fee, ape_distro, ape_router, ape_factory, minter)
    user = accounts[0]
    tx = ape_factory.createApeVault(usdc, '0x0000000000000000000000000000000000000000', {'from':user})
    ape_vault = ApeVaultWrapper.at(tx.new_contracts[0])
    circle = '0x1'
    ape_vault.approveCircleAdmin(circle, user, {'from':user})
    assert ape_distro.vaultApprovals(ape_vault, circle) == user
    ape_vault.approveCircleAdmin(circle, ape_vault, {'from':user})
    assert ape_distro.vaultApprovals(ape_vault, circle) == ape_vault

def test_tap_revert(ape_reg, ape_fee, ape_distro, ape_router, ape_factory, big_usdc, usdc, ApeVaultWrapper, minter, interface):
    setup_protocol(ape_reg, ape_fee, ape_distro, ape_router, ape_factory, minter)
    user = accounts[0]
    tx = ape_factory.createApeVault(usdc, '0x0000000000000000000000000000000000000000', {'from':user})
    ape_vault = ApeVaultWrapper.at(tx.new_contracts[0])
    circle = '0x1'
    with reverts(''):
        ape_vault.tap(10, 1, {'from':user})