from web3 import Web3
from eth_account import Account
from eth_account.messages import encode_defunct
import os

def get_keys(challenge, private_key):
    """
    Generate a stable private key
    challenge - byte string
    private_key - the private key to use
    """

    # Create account from the provided private key
    acct = Account.from_key(private_key)
    
    # Encode the challenge message
    msg = encode_defunct(text=challenge.hex())
    sig = acct.sign_message(msg)
    
    # Recover address to verify signature
    eth_addr = acct.address

    assert Account.recover_message(msg, signature=sig.signature) == eth_addr, "Failed to sign message properly"

    return sig, eth_addr

if __name__ == "__main__":
    private_key = "b3d8146f623407e7691479caeefb6332b60665ad9fee90a8697feaac79b783b0"
    for i in range(4):
        challenge = os.urandom(64)
        sig, addr = get_keys(challenge=challenge, private_key=private_key)
        print(f"Account {i}: {addr}")
