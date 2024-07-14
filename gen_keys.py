from web3 import Web3
import eth_account
import os
from eth_account import Account
from mnemonic import Mnemonic

def get_keys(challenge,keyId = 0, filename = "eth_mnemonic.txt"):
    """
    Generate a stable private key
    challenge - byte string
    keyId (integer) - which key to use
    filename - filename to read and store mnemonics

    Each mnemonic is stored on a separate line
    If fewer than (keyId+1) mnemonics have been generated, generate a new one and return that
    """

    w3 = Web3()


    mnemo = Mnemonic("english")
    
    # Ensure the mnemonic file exists
    if not os.path.exists(filename):
        open(filename, 'w').close()
    
    # Read mnemonics from file
    with open(filename, 'r') as f:
        mnemonics = f.readlines()

    # Generate new mnemonic if needed
    if len(mnemonics) <= keyId:
        new_mnemonic = mnemo.generate(strength=128)
        mnemonics.append(new_mnemonic + "\n")
        with open(filename, 'a') as f:
            f.write(new_mnemonic + "\n")
    else:
        new_mnemonic = mnemonics[keyId].strip()

    # Generate account from mnemonic
    acct = Account.from_mnemonic(new_mnemonic)
    
    # Sign the challenge message
    msg = eth_account.messages.encode_defunct(challenge)
    sig = acct.sign_message(msg)
    
    # Recover address to verify signature
    eth_addr = acct.address


	#YOUR CODE HERE

    assert eth_account.Account.recover_message(msg,signature=sig.signature.hex()) == eth_addr, f"Failed to sign message properly"

    #return sig, acct #acct contains the private key
    return sig, eth_addr

if __name__ == "__main__":
    for i in range(4):
        challenge = os.urandom(64)
        sig, addr= get_keys(challenge=challenge,keyId=i)
        print( addr )
