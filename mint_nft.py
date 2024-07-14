from web3 import Web3
import random

# Connect to Avalanche Fuji Testnet
w3 = Web3(Web3.HTTPProvider('https://api.avax-test.network/ext/bc/C/rpc'))

# Replace with your private key
private_key = "b3d8146f623407e7691479caeefb6332b60665ad9fee90a8697feaac79b783b0"
acct = w3.eth.account.from_key(private_key)

# Contract details
contract_address = "0x85ac2e065d4526FBeE6a2253389669a12318A412"
abi = [
    {
        "constant": False,
        "inputs": [
            {
                "name": "nonce",
                "type": "uint256"
            }
        ],
        "name": "claim",
        "outputs": [],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

# Create contract instance
contract = w3.eth.contract(address=contract_address, abi=abi)

# Function to mint NFT
def mint_nft():
    nonce = w3.eth.getTransactionCount(acct.address)
    nonce_value = random.randint(1, 1e6)  # Generate a random nonce

    print(f"Nonce value: {nonce_value}")

    txn = contract.functions.claim(nonce_value).buildTransaction({
        'chainId': 43113,  # Chain ID for Avalanche Fuji Testnet
        'gas': 2000000,
        'gasPrice': w3.toWei('50', 'gwei'),
        'nonce': nonce,
    })

    signed_txn = w3.eth.account.sign_transaction(txn, private_key=private_key)
    tx_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)

    print(f"Transaction sent with hash: {tx_hash.hex()}")

    # Wait for the transaction receipt
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    print(f"Transaction receipt: {tx_receipt}")

if __name__ == '__main__':
    mint_nft()
