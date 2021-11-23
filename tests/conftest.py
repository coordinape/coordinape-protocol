import pytest
import csv

@pytest.fixture(scope="function", autouse=True)
def shared_setup(fn_isolation):
    pass

@pytest.fixture()
def minter(accounts):
    return accounts[0]

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
    return ApeRegistry.deploy(0, {'from':minter})

@pytest.fixture()
def ape_factory(ApeVaultFactory, ape_reg, yearn_reg, minter):
    return ApeVaultFactory.deploy(yearn_reg, ape_reg, {'from':minter})

@pytest.fixture()
def ape_router(ApeRouter, yearn_reg, ape_factory, minter):
    return ApeRouter.deploy(yearn_reg, ape_factory, 0, {'from':minter})

@pytest.fixture()
def ape_distro(ApeDistributor, minter):
    return ApeDistributor.deploy({'from':minter})

@pytest.fixture()
def ape_fee(FeeRegistry, minter):
    return FeeRegistry.deploy({'from':minter})

@pytest.fixture()
def implementation(ApeVaultWrapperImplementation, minter):
    return ApeVaultWrapperImplementation.deploy({'from':minter})

@pytest.fixture()
def beacon(ApeUgradeableBeacon, minter, implementation):
    return ApeUgradeableBeacon.deploy(implementation, 0, {'from':minter})

@pytest.fixture()
def registry_beacon(ApeRegistryBeacon, minter, implementation):
    return ApeRegistryBeacon.deploy(implementation, 0, {'from':minter})

@pytest.fixture()
def ape_factory_beacon(ApeVaultFactoryBeacon, ape_reg, yearn_reg, minter, beacon):
    return ApeVaultFactoryBeacon.deploy(yearn_reg, ape_reg, beacon, {'from':minter})

@pytest.fixture()
def ape_factory_registry_beacon(ApeVaultFactoryBeacon, ape_reg, yearn_reg, minter, registry_beacon):
    return ApeVaultFactoryBeacon.deploy(yearn_reg, ape_reg, registry_beacon, {'from':minter})

@pytest.fixture()
def ape_router_beacon(ApeRouter, yearn_reg, ape_factory_beacon, minter):
    return ApeRouter.deploy(yearn_reg, ape_factory_beacon, 0, {'from':minter})

@pytest.fixture()
def ape_router_registry_beacon(ApeRouter, yearn_reg, ape_factory_registry_beacon, minter):
    return ApeRouter.deploy(yearn_reg, ape_factory_registry_beacon, 0, {'from':minter})

@pytest.fixture()
def mock_yearn_reg(MockRegistry, minter):
    return MockRegistry.deploy({'from':minter})

@pytest.fixture()
def mock_yearn_vault_factories(MockVaultFactory, mock_yearn_reg, minter):
    return MockVaultFactory.deploy(mock_yearn_reg, {'from':minter})

@pytest.fixture()
def mock_ape_reg(ApeRegistry, minter):
    return ApeRegistry.deploy(0, {'from':minter})

@pytest.fixture()
def mock_ape_factory(ApeVaultFactory, mock_ape_reg, mock_yearn_reg, minter):
    return ApeVaultFactory.deploy(mock_yearn_reg, mock_ape_reg, {'from':minter})

@pytest.fixture()
def mock_ape_router(ApeRouter, mock_yearn_reg, mock_ape_factory, minter):
    return ApeRouter.deploy(mock_yearn_reg, mock_ape_factory, 0, {'from':minter})

@pytest.fixture()
def mock_ape_distro(ApeDistributor, minter):
    return ApeDistributor.deploy({'from':minter})

@pytest.fixture()
def mock_ape_fee(FeeRegistry, minter):
    return FeeRegistry.deploy({'from':minter})


@pytest.fixture()
def implementation1(ApeVaultWrapperImplementation1, minter):
    return ApeVaultWrapperImplementation1.deploy({'from':minter})

@pytest.fixture()
def implementation2(ApeVaultWrapperImplementation2, minter):
    return ApeVaultWrapperImplementation2.deploy({'from':minter})

@pytest.fixture()
def implementation3(ApeVaultWrapperImplementation3, minter):
    return ApeVaultWrapperImplementation3.deploy({'from':minter})

@pytest.fixture()
def mock_registry_beacon(ApeRegistryBeacon, minter, implementation1):
    return ApeRegistryBeacon.deploy(implementation1, 0, {'from':minter})

@pytest.fixture()
def mock_factory_registry_beacon(MockVaultFactoryBeacon, ape_reg, yearn_reg, minter, mock_registry_beacon):
    return MockVaultFactoryBeacon.deploy(yearn_reg, ape_reg, mock_registry_beacon, {'from':minter})
