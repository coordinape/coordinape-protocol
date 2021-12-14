from brownie import accounts, chain, reverts, Wei
from eth_account.messages import encode_defunct, encode_intended_validator, SignableMessage
from eth_abi import encode_single
import web3

def test_normal_implementation(mock_factory_registry_beacon, accounts, ApeVaultWrapperImplementation1):
	user = accounts[0]
	tx = mock_factory_registry_beacon.createApeVault({'from':user})
	imp = ApeVaultWrapperImplementation1.at(tx.new_contracts[0])
	assert imp.someValue() == 0
	assert imp.version() == 1
	imp.write({'from':user})
	assert imp.someValue() == 11

def test_upgrade(mock_factory_registry_beacon, mock_registry_beacon, accounts, ApeVaultWrapperImplementation1, implementation2, implementation3, minter):
	user = accounts[0]
	tx = mock_factory_registry_beacon.createApeVault({'from':user})
	imp = ApeVaultWrapperImplementation1.at(tx.new_contracts[0])
	imp.write({'from':user})
	assert imp.someValue() == 11
	call = mock_registry_beacon.pushNewImplementation.encode_input(implementation2)
	mock_registry_beacon.schedule(mock_registry_beacon, call, '', '', 0, {'from':minter})
	mock_registry_beacon.execute(mock_registry_beacon, call, '', '', 0, {'from':minter})
	assert imp.someValue() == 11
	assert imp.version() == 2
	imp.write({'from':user})
	assert imp.someValue() == 22
	call = mock_registry_beacon.pushNewImplementation.encode_input(implementation3)
	mock_registry_beacon.schedule(mock_registry_beacon, call, '', '', 0, {'from':minter})
	mock_registry_beacon.execute(mock_registry_beacon, call, '', '', 0, {'from':minter})
	assert imp.someValue() == 22
	assert imp.version() == 3
	imp.write({'from':user})
	assert imp.someValue() == 33

def test_opt_out(mock_factory_registry_beacon, mock_registry_beacon, accounts, ApeVaultWrapperImplementation1, ApeBeacon, implementation2, implementation3, minter):
	user = accounts[0]
	disc = ApeBeacon.deploy(mock_registry_beacon, user, '0xe1c7392a', {'from':user})
	pref_call = disc.setBeaconDeploymentPrefs.encode_input(1)
	tx = mock_factory_registry_beacon.createApeVault({'from':user})
	imp = ApeVaultWrapperImplementation1.at(tx.new_contracts[0])
	imp.write({'from':user})
	assert imp.someValue() == 11
	user.transfer(to=imp, amount=0, data=pref_call)
	assert mock_registry_beacon.deploymentPref(imp) == 1
	call = mock_registry_beacon.pushNewImplementation.encode_input(implementation2)
	mock_registry_beacon.schedule(mock_registry_beacon, call, '', '', 0, {'from':minter})
	mock_registry_beacon.execute(mock_registry_beacon, call, '', '', 0, {'from':minter})
	assert imp.someValue() == 11
	assert imp.version() == 1
	imp.write({'from':user})
	assert imp.someValue() == 11
	call = mock_registry_beacon.pushNewImplementation.encode_input(implementation3)
	mock_registry_beacon.schedule(mock_registry_beacon, call, '', '', 0, {'from':minter})
	mock_registry_beacon.execute(mock_registry_beacon, call, '', '', 0, {'from':minter})
	assert imp.someValue() == 11
	assert imp.version() == 1
	imp.write({'from':user})
	assert imp.someValue() == 11
	pref_call = disc.setBeaconDeploymentPrefs.encode_input(3)
	user.transfer(to=imp, amount=0, data=pref_call)
	assert imp.someValue() == 11
	assert imp.version() == 3
	imp.write({'from':user})
	assert imp.someValue() == 33

def test_opt_out_then_opt_in(mock_factory_registry_beacon, mock_registry_beacon, accounts, ApeVaultWrapperImplementation1, ApeBeacon, implementation2, implementation3, minter):
	user = accounts[0]
	disc = ApeBeacon.deploy(mock_registry_beacon, user, '0xe1c7392a', {'from':user})
	pref_call = disc.setBeaconDeploymentPrefs.encode_input(1)
	tx = mock_factory_registry_beacon.createApeVault({'from':user})
	add = tx.new_contracts[0]
	imp = ApeVaultWrapperImplementation1.at(add)
	imp.write({'from':user})
	assert imp.someValue() == 11
	user.transfer(to=imp, amount=0, data=pref_call)
	assert mock_registry_beacon.deploymentPref(imp) == 1
	call = mock_registry_beacon.pushNewImplementation.encode_input(implementation2)
	mock_registry_beacon.schedule(mock_registry_beacon, call, '', '', 0, {'from':minter})
	mock_registry_beacon.execute(mock_registry_beacon, call, '', '', 0, {'from':minter})
	assert imp.someValue() == 11
	assert imp.version() == 1
	imp.write({'from':user})
	assert imp.someValue() == 11
	pref_call = disc.setBeaconDeploymentPrefs.encode_input(0)
	user.transfer(to=imp, amount=0, data=pref_call)
	call = mock_registry_beacon.pushNewImplementation.encode_input(implementation3)
	mock_registry_beacon.schedule(mock_registry_beacon, call, '', '', 0, {'from':minter})
	mock_registry_beacon.execute(mock_registry_beacon, call, '', '', 0, {'from':minter})
	assert imp.someValue() == 11
	assert imp.version() == 3
	imp.write({'from':user})
	assert imp.someValue() == 33