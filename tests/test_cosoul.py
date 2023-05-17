from brownie import accounts, chain, Wei, web3
from eth_account.messages import encode_defunct, encode_intended_validator, SignableMessage
from eth_abi import encode_single

def padded_hex(i, l, prefix=True):
    _hex = hex(i)[2:] # remove '0x' from beginning of str
    hex_len = len(_hex)
    extra = '0' * (l - hex_len)
    pre = '0x'
    if not prefix:
        pre = ''
        return (pre + _hex if hex_len == l else
                '?' * l if hex_len > l else
                pre + extra + _hex if hex_len < l else
                None)

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

def test_update_optimized(cosoul, minter):
    ids = [10,101,1010,10101]
    amounts = [45,46,47,48,49]
    payload = '0x00'
    for amount, id in zip(amounts, ids):
        payload += padded_hex(amount, 8, False) + padded_hex(id, 8, False)

    # print(payload)
    cosoul.batchSetSlot_UfO(payload, {'from':minter})
    
    for amount, id in zip(amounts, ids):
        assert cosoul.getSlot(0, id) == amount