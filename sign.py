import eth_account
from web3 import Web3
from eth_account.messages import encode_defunct


def sign(m):
    w3 = Web3()
    # create an eth account and recover the address (derived from the public key) and private key
    # your code here

    eth_address = '0x3b7f6e8011Bc2137ea1Aca77fAeDbe84Af46374A'  # Eth account
    private_key = 'b3d8146f623407e7691479caeefb6332b60665ad9fee90a8697feaac79b783b0'

    # Correct way to create an account using the private key
    account = eth_account.Account.from_key(private_key)

    # Generate the message to be signed
    message = encode_defunct(text=m)

    # generate signature
    # your code here

    signed_message = w3.eth.account.sign_message(message, private_key)

    assert isinstance(signed_message, eth_account.datastructures.SignedMessage)

    return eth_address, signed_message
