from brownie import accounts, chain, reverts, Wei
import json

TAP_BASE = 1
TAP_PROFIT = 0

def setup_protocol(ape_reg, ape_fee, ape_distro, ape_router, ape_factory, minter):
    set_fee_call = ape_reg.setFeeRegistry.encode_input(ape_fee)
    set_router_call = ape_reg.setRouter.encode_input(ape_router)
    set_distro_call = ape_reg.setDistributor.encode_input(ape_distro)
    set_factory_call = ape_reg.setFactory.encode_input(ape_factory)
    ape_reg.schedule(ape_reg, set_fee_call, '', '', 0, {'from':minter})
    ape_reg.schedule(ape_reg, set_router_call, '', '', 0, {'from':minter})
    ape_reg.schedule(ape_reg, set_distro_call, '', '', 0, {'from':minter})
    ape_reg.schedule(ape_reg, set_factory_call, '', '', 0, {'from':minter})
    ape_reg.execute(ape_reg, set_fee_call, '', '', 0, {'from':minter})
    ape_reg.execute(ape_reg, set_router_call, '', '', 0, {'from':minter})
    ape_reg.execute(ape_reg, set_distro_call, '', '', 0, {'from':minter})
    ape_reg.execute(ape_reg, set_factory_call, '', '', 0, {'from':minter})

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

def test_allowance_revert(ape_reg, ape_fee, ape_distro, ape_router, ape_factory, big_usdc, usdc, ApeVaultWrapper, minter, interface):
    setup_protocol(ape_reg, ape_fee, ape_distro, ape_router, ape_factory, minter)
    user = accounts[0]
    amount = 1_000_000_000_000
    usdc.transfer(user, amount, {'from':big_usdc})
    usdc.approve(ape_router, 2 ** 256 -1, {'from':user})
    tx = ape_factory.createApeVault(usdc, '0x0000000000000000000000000000000000000000', {'from':user})
    ape_vault = ApeVaultWrapper.at(tx.new_contracts[0])
    ape_router.delegateDeposit(ape_vault, usdc, amount, {'from':user})
    usdc_vault = interface.IERC20('0x5f18C75AbDAe578b483E5F43f12a39cF75b973a9')
    circle = '0x0000000000000000000000000000000000000001'
    token = usdc
    grant = Wei('20_000_000_000')
    interval = 60 * 60 * 24 * 14 # 14 days
    epochs = 4
    root = '0x1838e0c6251730868cce6768e2062af0e72f79409a1f7011351bd2c1535e2a5c'
    ape_vault.updateAllowance(circle, token, grant, interval, epochs, {'from':user})
    admin = accounts[1]
    ape_vault.approveCircleAdmin(circle, admin, {'from':user})
    with reverts('Sender cannot upload a root'):
        ape_distro.uploadEpochRoot(ape_vault, circle, token, root, grant, TAP_BASE, {'from': accounts[2]})
    ape_distro.uploadEpochRoot(ape_vault, circle, token, root, grant // 2, TAP_BASE, {'from': admin})
    assert usdc_vault.balanceOf(ape_distro) == grant
    assert ape_distro.epochRoots(circle, token, 0) == root
    with reverts('Circle does not have sufficient allowance'):
        ape_distro.uploadEpochRoot(ape_vault, circle, token, root, grant // 2 + 1, TAP_BASE, {'from': admin})
    # spend epoch count allowance
    ape_distro.uploadEpochRoot(ape_vault, circle, token, root, grant // 8, TAP_BASE, {'from': admin})
    ape_distro.uploadEpochRoot(ape_vault, circle, token, root, grant // 8, TAP_BASE, {'from': admin})
    ape_distro.uploadEpochRoot(ape_vault, circle, token, root, grant // 8, TAP_BASE, {'from': admin})
    with reverts('Circle cannot tap anymore'):
        ape_distro.uploadEpochRoot(ape_vault, circle, token, root, grant // 2 + 1, TAP_BASE, {'from': admin})

def test_allowance_interval(ape_reg, ape_fee, ape_distro, ape_router, ape_factory, big_usdc, usdc, ApeVaultWrapper, minter, interface, chain):
    setup_protocol(ape_reg, ape_fee, ape_distro, ape_router, ape_factory, minter)
    user = accounts[0]
    amount = 1_000_000_000_000
    usdc.transfer(user, amount, {'from':big_usdc})
    usdc.approve(ape_router, 2 ** 256 -1, {'from':user})
    tx = ape_factory.createApeVault(usdc, '0x0000000000000000000000000000000000000000', {'from':user})
    ape_vault = ApeVaultWrapper.at(tx.new_contracts[0])
    ape_router.delegateDeposit(ape_vault, usdc, amount, {'from':user})
    usdc_vault = interface.IERC20('0x5f18C75AbDAe578b483E5F43f12a39cF75b973a9')
    circle = '0x0000000000000000000000000000000000000001'
    token = usdc
    grant = Wei('20_000_000_000')
    interval = 60 * 60 * 24 * 14 # 14 days
    epochs = 4
    root = '0x1838e0c6251730868cce6768e2062af0e72f79409a1f7011351bd2c1535e2a5c'
    ape_vault.updateAllowance(circle, token, grant, interval, epochs, {'from':user})
    admin = accounts[1]
    ape_vault.approveCircleAdmin(circle, admin, {'from':user})
    with reverts('Sender cannot upload a root'):
        ape_distro.uploadEpochRoot(ape_vault, circle, token, root, grant, TAP_BASE, {'from': accounts[2]})
    ape_distro.uploadEpochRoot(ape_vault, circle, token, root, grant // 2, TAP_BASE, {'from': admin})
    assert usdc_vault.balanceOf(ape_distro) == grant
    assert ape_distro.epochRoots(circle, token, 0) == root
    with reverts('Circle does not have sufficient allowance'):
        ape_distro.uploadEpochRoot(ape_vault, circle, token, root, grant // 2 + 1, TAP_BASE, {'from': admin})
    chain.sleep(interval + 1)
    ape_distro.uploadEpochRoot(ape_vault, circle, token, root, grant, TAP_BASE, {'from': admin})
    with reverts('Circle does not have sufficient allowance'):
        ape_distro.uploadEpochRoot(ape_vault, circle, token, root, grant // 2 + 1, TAP_BASE, {'from': admin})

def test_claiming(ape_reg, ape_fee, ape_distro, ape_router, ape_factory, big_usdc, usdc, ApeVaultWrapper, minter, interface):
    setup_protocol(ape_reg, ape_fee, ape_distro, ape_router, ape_factory, minter)
    user = accounts[0]
    amount = 1_000_000_000_000
    usdc.transfer(user, amount, {'from':big_usdc})
    usdc.approve(ape_router, 2 ** 256 -1, {'from':user})
    tx = ape_factory.createApeVault(usdc, '0x0000000000000000000000000000000000000000', {'from':user})
    ape_vault = ApeVaultWrapper.at(tx.new_contracts[0])
    ape_router.delegateDeposit(ape_vault, usdc, amount, {'from':user})
    usdc_vault = interface.IERC20('0x5f18C75AbDAe578b483E5F43f12a39cF75b973a9')
    circle = '0x0000000000000000000000000000000000000001'
    token = usdc
    grant = Wei('20_000_000_000')
    interval = 60 * 60 * 24 * 14 # 14 days
    epochs = 4
    root = '0x1838e0c6251730868cce6768e2062af0e72f79409a1f7011351bd2c1535e2a5c'
    ape_vault.updateAllowance(circle, token, grant, interval, epochs, {'from':user})
    admin = accounts[1]
    ape_vault.approveCircleAdmin(circle, admin, {'from':user})
    with reverts('Sender cannot upload a root'):
        ape_distro.uploadEpochRoot(ape_vault, circle, token, root, grant, TAP_BASE, {'from': accounts[2]})
    ape_distro.uploadEpochRoot(ape_vault, circle, token, root, grant // 2, TAP_BASE, {'from': admin})
    file = open('tests/merkle_test.json', 'r')
    tree = json.load(file)
    adds = [
        '0x0000000000000000000000000000000000000001',
        '0x0000000000000000000000000000000000000002',
        '0x0000000000000000000000000000000000000003',
        '0x0000000000000000000000000000000000000004',
        '0x0000000000000000000000000000000000000005'
    ]
    accs = [accounts.at(add, force=True) for add in adds]
    add_0_data = tree['claims'][adds[0]]
    with reverts('Wrong proof'):
        ape_distro.claim(circle, usdc_vault, 0, add_0_data['index'], adds[1], add_0_data['amount'], False, add_0_data['proof'], {'from':user})
    ape_distro.claim(circle, usdc_vault, 0, add_0_data['index'], adds[0], add_0_data['amount'], False, add_0_data['proof'], {'from':user})
    assert usdc_vault.balanceOf(adds[0]) == 2_000_000_000
    with reverts('Claimed already'):
        ape_distro.claim(circle, usdc_vault, 0, add_0_data['index'], adds[0], add_0_data['amount'], False, add_0_data['proof'], {'from':user})
    add_1_data = tree['claims'][adds[1]]
    ape_distro.claim(circle, usdc_vault, 0, add_1_data['index'], adds[1], add_1_data['amount'], True, add_1_data['proof'], {'from':user})
    assert usdc.balanceOf(adds[1]) >= 3_000_000_000
    assert ape_distro.checkpoints(circle, usdc_vault, adds[1]) == 3_000_000_000
