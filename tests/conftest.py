import pytest
import csv

@pytest.fixture(scope="function", autouse=True)
def shared_setup(fn_isolation):
    pass


@pytest.fixture()
def minter(accounts):
    return accounts[0]


@pytest.fixture()
def coco(accounts):
    return accounts.at("0x721931508df2764fd4f70c53da646cb8aed16ace", force=True)

@pytest.fixture()
def myo(accounts):
    return accounts.at("0x8d8203f7f9137c9d59f0cf64e9af38f4df8f487f", force=True)


@pytest.fixture()
def big(accounts):
    return accounts.at("0x742d35cc6634c0532925a3b844bc454e4438f44e", force=True)

@pytest.fixture()
def usdc(interface):
    return interface.IERC20('0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48')

@pytest.fixture()
def big_usdc(accounts):
    return accounts.at("0x47ac0fb4f2d84898e4d9e7b4dab3c24507a6d503", force=True)

@pytest.fixture()
def yearn_reg():
    return '0x50c1a2ea0a861a967d9d0ffe2ae4012c2e053804'

@pytest.fixture()
def ape_reg(ApeRegistry, minter):
    return ApeRegistry.deploy({'from':minter})

@pytest.fixture()
def ape_factory(ApeVaultFactory, ape_reg, yearn_reg, minter):
    return ApeVaultFactory.deploy(yearn_reg, ape_reg, {'from':minter})

@pytest.fixture()
def ape_router(ApeRouter, yearn_reg, ape_factory, minter):
    return ApeRouter.deploy(yearn_reg, ape_factory, {'from':minter})

@pytest.fixture()
def ape_distro(ApeDistributor, minter):
    return ApeDistributor.deploy({'from':minter})

@pytest.fixture()
def ape_fee(FeeRegistry, minter):
    return FeeRegistry.deploy({'from':minter})

# @pytest.fixture()
# def ape_reg(ape_reg_, ape_factory, ape_router, ape_fee, ape_distro, minter):
#     ape_reg_.setFeeRegistry(ape_fee, {'from':minter})
#     ape_reg_.setRouter(ape_router, {'from':minter})
#     ape_reg_.setDistributor(ape_distro, {'from':minter})
#     ape_reg_.setFactory(ape_factory, {'from':minter})
#     return ape_reg_
