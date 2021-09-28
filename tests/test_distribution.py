from brownie import accounts, chain, reverts, Wei

TAP_BASE = 1
TAP_PROFIT = 0

def setup_protocol(ape_reg, ape_fee, ape_distro, ape_router, ape_factory, minter):
    ape_reg.setFeeRegistry(ape_fee, {'from':minter})
    ape_reg.setRouter(ape_router, {'from':minter})
    ape_reg.setDistributor(ape_distro, {'from':minter})
    ape_reg.setFactory(ape_factory, {'from':minter})

def test_root_upload(ape_reg, ape_fee, ape_distro, ape_router, ape_factory, big_usdc, usdc, ApeVaultWrapper, minter, interface):
    setup_protocol(ape_reg, ape_fee, ape_distro, ape_router, ape_factory, minter)
    user = accounts[0]
    amount = 1_000_000_000_000
    usdc.transfer(user, amount, {'from':big_usdc})
    usdc.approve(ape_router, 2 ** 256 -1, {'from':user})
    tx = ape_factory.createApeVault(usdc, '0x0000000000000000000000000000000000000000', {'from':user})
    ape_vault = ApeVaultWrapper.at(tx.new_contracts[0])
    ape_router.delegateDeposit(ape_vault, usdc, amount, {'from':user})
    usdc_vault = interface.IERC20('0x5f18C75AbDAe578b483E5F43f12a39cF75b973a9')
    assert usdc_vault.balanceOf(ape_vault) >= Wei('20_000_000_000')
    circle = '0x0000000000000000000000000000000000000001'
    token = usdc
    grant = Wei('20_000_000_000')
    interval = 60 * 60 * 14 # 14 days
    epochs = 4
    root = '0x1838e0c6251730868cce6768e2062af0e72f79409a1f7011351bd2c1535e2a5c'
    ape_vault.updateAllowance(circle, token, grant, interval, epochs, {'from':user})
    admin = accounts[1]
    ape_vault.approveCircleAdmin(circle, admin, {'from':user})
    with reverts('Sender cannot upload a root'):
        ape_distro.uploadEpochRoot(ape_vault, circle, token, root, grant, TAP_BASE, {'from': accounts[2]})
    ape_distro.uploadEpochRoot(ape_vault, circle, token, root, grant, TAP_BASE, {'from': admin})
    assert usdc_vault.balanceOf(ape_distro) == grant
    assert ape_distro.epochRoots(circle, token, 0) == root