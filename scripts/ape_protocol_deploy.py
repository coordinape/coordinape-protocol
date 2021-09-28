from brownie import accounts, chain, ApeVaultWrapper, ApeVaultFactory, ApeDistributor, ApeRegistry, ApeRouter, FeeRegistry

def deploy_protocol():
	user = accounts.load('moist')
	yearn_reg = ''
	ape_reg = ApeRegistry.deploy({'from':user})
	ape_factory = ApeVaultFactory.deploy(yearn_reg, ape_reg, {'from':user})
	ape_router = ApeRouter.deploy(yearn_reg, ape_factory, {'from':user})
	ape_distro = ApeDistributor.deploy({'from':user})
	ape_fee = FeeRegistry.deploy({'from':user})

	ape_reg.setFeeRegistry(ape_fee, {'from':user})
	ape_reg.setRouter(ape_router, {'from':user})
	ape_reg.setDistributor(ape_distro, {'from':user})
	ape_reg.setFactory(ape_factory, {'from':user})

