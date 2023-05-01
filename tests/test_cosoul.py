from brownie import accounts, chain, Wei, web3
from eth_account.messages import encode_defunct, encode_intended_validator, SignableMessage
from eth_abi import encode_single


def generate_mint_sig(user, nonce):
    signer = accounts.from_mnemonic('noise just dawn civil drum cause crawl major episode same retreat divorce', offset=2)
    base_message = web3.soliditySha3(
                [ 'address' , 'uint256' ] , 
                [user, nonce])
    message = encode_defunct(base_message)
    return web3.eth.account.sign_message(message, signer.private_key)

def test_update(cosoul, minter):
    sig = generate_mint_sig(accounts[4].address, 0)
    cosoul.mintWithSignature(0, sig.signature, {'from':accounts[4]})
    assert cosoul.balanceOf(accounts[4]) == 1