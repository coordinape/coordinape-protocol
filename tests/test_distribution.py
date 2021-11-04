from brownie import accounts, chain, reverts, Wei
import json

TAP_BASE = 1
TAP_PROFIT = 0

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
    circle = '0x1'
    token = usdc_vault
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
    circle = '0x1'
    token = usdc_vault
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
    assert usdc_vault.balanceOf(ape_distro) == grant // 2
    assert ape_distro.epochRoots(circle, token, 0) == root
    with reverts('Circle does not have sufficient allowance'):
        ape_distro.uploadEpochRoot(ape_vault, circle, token, root, grant // 2 + 1, TAP_BASE, {'from': admin})
    # spend epoch count allowance
    ape_distro.uploadEpochRoot(ape_vault, circle, token, root, grant // 8, TAP_BASE, {'from': admin})
    ape_distro.uploadEpochRoot(ape_vault, circle, token, root, grant // 8, TAP_BASE, {'from': admin})
    ape_distro.uploadEpochRoot(ape_vault, circle, token, root, grant // 8, TAP_BASE, {'from': admin})
    with reverts('Circle does not have sufficient allowance'):
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
    circle = '0x1'
    token = usdc_vault
    grant = Wei('20_000_000_000')
    interval = 60 * 60 * 24 * 14 # 14 days
    epochs = 5
    root = '0x1838e0c6251730868cce6768e2062af0e72f79409a1f7011351bd2c1535e2a5c'
    ape_vault.updateAllowance(circle, token, grant, interval, epochs, {'from':user})
    admin = accounts[1]
    ape_vault.approveCircleAdmin(circle, admin, {'from':user})
    with reverts('Sender cannot upload a root'):
        ape_distro.uploadEpochRoot(ape_vault, circle, token, root, grant, TAP_BASE, {'from': accounts[2]})
    ape_distro.uploadEpochRoot(ape_vault, circle, token, root, grant // 2, TAP_BASE, {'from': admin})

    assert usdc_vault.balanceOf(ape_distro) == grant // 2
    assert ape_distro.epochRoots(circle, token, 0) == root
    
    with reverts('Circle does not have sufficient allowance'):
        ape_distro.uploadEpochRoot(ape_vault, circle, token, root, grant // 2 + 1, TAP_BASE, {'from': admin})
    chain.sleep(interval + 1)
    ape_distro.uploadEpochRoot(ape_vault, circle, token, root, grant // 2, TAP_BASE, {'from': admin})
    with reverts('Circle does not have sufficient allowance'):
        ape_distro.uploadEpochRoot(ape_vault, circle, token, root, grant, TAP_BASE, {'from': admin})
    for i in range(4):
        chain.sleep(interval + 1)
        ape_distro.uploadEpochRoot(ape_vault, circle, token, root, grant, TAP_BASE, {'from': admin})
    chain.sleep(interval + 1)
    with reverts('Circle cannot tap anymore'):
        ape_distro.uploadEpochRoot(ape_vault, circle, token, root, grant // 2 + 1, TAP_BASE, {'from': admin})

def test_allowance_one_time(ape_reg, ape_fee, ape_distro, ape_router, ape_factory, big_usdc, usdc, ApeVaultWrapper, minter, interface, chain):
    setup_protocol(ape_reg, ape_fee, ape_distro, ape_router, ape_factory, minter)
    user = accounts[0]
    amount = 1_000_000_000_000
    usdc.transfer(user, amount, {'from':big_usdc})
    usdc.approve(ape_router, 2 ** 256 -1, {'from':user})
    tx = ape_factory.createApeVault(usdc, '0x0000000000000000000000000000000000000000', {'from':user})
    ape_vault = ApeVaultWrapper.at(tx.new_contracts[0])
    ape_router.delegateDeposit(ape_vault, usdc, amount, {'from':user})
    usdc_vault = interface.IERC20('0x5f18C75AbDAe578b483E5F43f12a39cF75b973a9')
    circle = '0x1'
    token = usdc_vault
    grant = Wei('20_000_000_000')
    interval = 60 * 60 * 24 * 14 # 14 days
    epochs = 0
    root = '0x1838e0c6251730868cce6768e2062af0e72f79409a1f7011351bd2c1535e2a5c'
    ape_vault.updateAllowance(circle, token, grant, interval, epochs, {'from':user})
    admin = accounts[1]
    ape_vault.approveCircleAdmin(circle, admin, {'from':user})
    with reverts('Sender cannot upload a root'):
        ape_distro.uploadEpochRoot(ape_vault, circle, token, root, grant, TAP_BASE, {'from': accounts[2]})
    ape_distro.uploadEpochRoot(ape_vault, circle, token, root, grant // 2, TAP_BASE, {'from': admin})

    assert usdc_vault.balanceOf(ape_distro) == grant // 2
    assert ape_distro.epochRoots(circle, token, 0) == root
    
    with reverts('Circle does not have sufficient allowance'):
        ape_distro.uploadEpochRoot(ape_vault, circle, token, root, grant // 2 + 1, TAP_BASE, {'from': admin})
    chain.sleep(interval + 1)
    with reverts('Circle cannot tap anymore'):
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
    circle = '0x1'
    token = usdc_vault
    grant = Wei('20_000_000_000')
    interval = 60 * 60 * 24 * 14 # 14 days
    epochs = 4
    root = '0x1838e0c6251730868cce6768e2062af0e72f79409a1f7011351bd2c1535e2a5c'
    ape_vault.updateAllowance(circle, token, grant, interval, epochs, {'from':user})
    admin = accounts[1]
    ape_vault.approveCircleAdmin(circle, admin, {'from':user})
    with reverts('Sender cannot upload a root'):
        ape_distro.uploadEpochRoot(ape_vault, circle, token, root, grant, TAP_BASE, {'from': accounts[2]})
    ape_distro.uploadEpochRoot(ape_vault, circle, token, root, grant, TAP_BASE, {'from': admin})
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
    print(usdc_vault.balanceOf(ape_distro))
    with reverts('Wrong proof'):
        ape_distro.claim(circle, usdc_vault, 0, add_0_data['index'], adds[1], add_0_data['amount'], False, add_0_data['proof'], {'from':user})
    ape_distro.claim(circle, usdc_vault, 0, add_0_data['index'], adds[0], add_0_data['amount'], False, add_0_data['proof'], {'from':user})
    assert usdc_vault.balanceOf(adds[0]) == 2_000_000_000
    with reverts('Claimed already'):
        ape_distro.claim(circle, usdc_vault, 0, add_0_data['index'], adds[0], add_0_data['amount'], False, add_0_data['proof'], {'from':user})
    add_1_data = tree['claims'][adds[1]]
    assert Wei(add_1_data['amount']) == 3_000_000_000
    pre = usdc.balanceOf(adds[1])
    ape_distro.claim(circle, usdc_vault, 0, add_1_data['index'], adds[1], add_1_data['amount'], True, add_1_data['proof'], {'from':adds[1]})
    assert usdc.balanceOf(adds[1]) - pre  >= 3_000_000_000
    assert ape_distro.checkpoints(circle, usdc_vault, adds[1]) == 3_000_000_000


def test_claiming_many(ape_reg, ape_fee, ape_distro, ape_router, ape_factory, big_usdc, usdc, ApeVaultWrapper, minter, interface):
    setup_protocol(ape_reg, ape_fee, ape_distro, ape_router, ape_factory, minter)
    user = accounts[0]
    amount = 1_000_000_000_000
    usdc.transfer(user, amount, {'from':big_usdc})
    usdc.approve(ape_router, 2 ** 256 -1, {'from':user})
    tx = ape_factory.createApeVault(usdc, '0x0000000000000000000000000000000000000000', {'from':user})
    ape_vault = ApeVaultWrapper.at(tx.new_contracts[0])
    ape_router.delegateDeposit(ape_vault, usdc, amount, {'from':user})
    usdc_vault = interface.IERC20('0x5f18C75AbDAe578b483E5F43f12a39cF75b973a9')
    circle = '0x1'
    token = usdc_vault
    grant = Wei('20_000_000_000')
    interval = 60 * 60 * 24 * 14 # 14 days
    epochs = 4
    root = '0x1838e0c6251730868cce6768e2062af0e72f79409a1f7011351bd2c1535e2a5c'
    ape_vault.updateAllowance(circle, token, grant, interval, epochs, {'from':user})
    admin = accounts[1]
    ape_vault.approveCircleAdmin(circle, admin, {'from':user})
    with reverts('Sender cannot upload a root'):
        ape_distro.uploadEpochRoot(ape_vault, circle, token, root, grant, TAP_BASE, {'from': accounts[2]})
    ape_distro.uploadEpochRoot(ape_vault, circle, token, root, grant, TAP_BASE, {'from': admin})
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
    circles = [circle for i in range(len(adds))]
    tokens = [usdc_vault for i in range(len(adds))]
    epochs_ = [0 for i in range(len(adds))]
    indexes = [tree['claims'][add]['index'] for add in adds]
    checkpoints = [tree['claims'][add]['amount'] for add in adds]
    redeems = [False for i in range(len(adds))]
    proofs = [tree['claims'][add]['proof'] for add in adds]
    add_0_data = tree['claims'][adds[0]]
    print(usdc_vault.balanceOf(ape_distro))
    print(len(circles))
    print(len(tokens + adds))
    print(len(epochs_ + indexes + checkpoints))
    print(len(redeems))
    print(len(proofs[1:]))
    with reverts('Wrong proof'):
        ape_distro.claimMany(circles, tokens + adds, epochs_ + indexes + checkpoints, redeems, proofs[1:], {'from':user})
    pre0 = usdc_vault.balanceOf(adds[0])
    pre1 = usdc_vault.balanceOf(adds[1])
    pre2 = usdc_vault.balanceOf(adds[2])
    pre3 = usdc_vault.balanceOf(adds[3])
    pre4 = usdc_vault.balanceOf(adds[4])
    ape_distro.claimMany(circles, tokens + adds, epochs_ + indexes + checkpoints, redeems, proofs, {'from':user})
    with reverts('Claimed already'):
        ape_distro.claim(circle, usdc_vault, 0, add_0_data['index'], adds[0], add_0_data['amount'], False, add_0_data['proof'], {'from':user})
    assert ape_distro.checkpoints(circle, usdc_vault, adds[1]) == 3_000_000_000
    assert usdc_vault.balanceOf(adds[0]) - pre0 == 2_000_000_000
    assert usdc_vault.balanceOf(adds[1]) - pre1 == 3_000_000_000
    assert usdc_vault.balanceOf(adds[2]) - pre2 == 4_000_000_000
    assert usdc_vault.balanceOf(adds[3]) - pre3 == 5_000_000_000
    assert usdc_vault.balanceOf(adds[4]) - pre4 == 6_000_000_000
