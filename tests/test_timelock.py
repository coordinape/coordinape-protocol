from brownie import accounts, chain, reverts, Wei
from eth_account.messages import encode_defunct, encode_intended_validator, SignableMessage
from eth_abi import encode_single
import web3

def setup_protocol(ape_reg, ape_fee, ape_distro, ape_router_registry_beacon, ape_factory_registry_beacon, minter):
    set_fee_call = ape_reg.setFeeRegistry.encode_input(ape_fee)
    set_router_call = ape_reg.setRouter.encode_input(ape_router_registry_beacon)
    set_distro_call = ape_reg.setDistributor.encode_input(ape_distro)
    set_factory_call = ape_reg.setFactory.encode_input(ape_factory_registry_beacon)
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

def test_timelock(ape_reg, ape_fee, ape_distro, ape_router_registry_beacon, ape_factory_registry_beacon, big_usdc, usdc, ApeVaultWrapperImplementation, minter, chain, web3):
    setup_protocol(ape_reg, ape_fee, ape_distro, ape_router_registry_beacon, ape_factory_registry_beacon, minter)
    assert ape_reg.factory() == ape_factory_registry_beacon
    assert ape_reg.feeRegistry() == ape_fee
    assert ape_reg.distributor() == ape_distro
    assert ape_reg.router() == ape_router_registry_beacon
    min_delay_call = ape_reg.changeMinDelay.encode_input(60*60*24)
    ape_reg.schedule(ape_reg, min_delay_call, '', '', 0, {'from':minter})
    ape_reg.execute(ape_reg, min_delay_call, '', '', 0, {'from':minter})
    assert ape_reg.minDelay() == 60 * 60 * 24
    with reverts('TimeLock: Caller is not contract itself'):
        ape_reg.changeMinDelay(0, {'from':minter})
    set_router_call = ape_reg.setRouter.encode_input(ape_reg)
    with reverts('TimeLock: Insufficient delay'):
        ape_reg.schedule(ape_reg, set_router_call, '', web3.keccak(text='test_timelock'), 60 * 60 * 23 , {'from':minter})
    ape_reg.schedule(ape_reg, set_router_call, '', web3.keccak(text='test_timelock'), 60 * 60 * 24 * 2 , {'from':minter})
    with reverts('TimeLock: Call already scheduled'):
        ape_reg.schedule(ape_reg, set_router_call, '', web3.keccak(text='test_timelock'), 60 * 60 * 24 * 2 , {'from':minter})
    with reverts('TimeLock: Not ready for execution'):
        ape_reg.execute(ape_reg, set_router_call, '', web3.keccak(text='test_timelock'), 60 * 60 * 24 * 2 , {'from':minter})
    chain.sleep(60 * 60 * 24 * 2 + 1)
    ape_reg.execute(ape_reg, set_router_call, '', web3.keccak(text='test_timelock'), 60 * 60 * 24 * 2 , {'from':minter})
    assert ape_reg.router() == ape_reg
    with reverts('TimeLock: Already executed'):
        ape_reg.execute(ape_reg, set_router_call, '', web3.keccak(text='test_timelock'), 60 * 60 * 24 * 2 , {'from':minter})
