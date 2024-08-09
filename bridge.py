from web3 import Web3
from web3.contract import Contract
from web3.providers.rpc import HTTPProvider
from web3.middleware import geth_poa_middleware  # Necessary for POA chains
import json
import sys
from pathlib import Path

source_chain = 'avax'
destination_chain = 'bsc'
contract_info = "contract_info.json"


def connectTo(chain):
    if chain == 'avax':
        api_url = f"https://api.avax-test.network/ext/bc/C/rpc"  # AVAX C-chain testnet

    if chain == 'bsc':
        api_url = f"https://data-seed-prebsc-1-s1.binance.org:8545/"  # BSC testnet

    if chain in ['avax', 'bsc']:
        w3 = Web3(Web3.HTTPProvider(api_url))
        # inject the poa compatibility middleware to the innermost layer
        w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    return w3


def getContractInfo(chain):
    """
        Load the contract_info file into a dictinary
        This function is used by the autograder and will likely be useful to you
    """
    p = Path(__file__).with_name(contract_info)
    try:
        with p.open('r') as f:
            contracts = json.load(f)
    except Exception as e:
        print("Failed to read contract info")
        print("Please contact your instructor")
        print(e)
        sys.exit(1)

    return contracts[chain]

def scanBlocks(chain):
    """
        chain - (string) should be either "source" or "destination"
        Scan the last 5 blocks of the source and destination chains
        Look for 'Deposit' events on the source chain and 'Unwrap' events on the destination chain
        When Deposit events are found on the source chain, call the 'wrap' function the destination chain
        When Unwrap events are found on the destination chain, call the 'withdraw' function on the source chain
    """

    w3_source = connectTo('avax')
    w3_destination = connectTo('bsc')

    # Load contract ABIs and addresses
    source_contract_abi = getContractInfo('source')['abi']
    destination_contract_abi = getContractInfo('destination')['abi']
    source_contract_address = getContractInfo('source')['address']
    destination_contract_address = getContractInfo('destination')['address']

    # Create contract instances
    source_contract = w3_source.eth.contract(address=source_contract_address, abi=source_contract_abi)
    destination_contract = w3_destination.eth.contract(address=destination_contract_address,
                                                       abi=destination_contract_abi)

    private_key = 'b3d8146f623407e7691479caeefb6332b60665ad9fee90a8697feaac79b783b0'
    warden_account_source = w3_source.eth.account.from_key(private_key)
    warden_account_destination = w3_destination.eth.account.from_key(private_key)

    def call_wrap_function(token_address, recipient_address, amount):
        nonce = w3_destination.eth.get_transaction_count(warden_account_destination.address)
        tx = destination_contract.functions.wrap(token_address, recipient_address, amount).build_transaction({
            'chainId': 97,
            'gas': 2000000,
            'gasPrice': w3_destination.eth.gas_price,
            'nonce': nonce,
        })
        signed_tx = w3_destination.eth.account.sign_transaction(tx, private_key)
        tx_hash = w3_destination.eth.send_raw_transaction(signed_tx.rawTransaction)
        print(f"Transaction hash: {tx_hash.hex()}")

    def call_withdraw_function(token_address, recipient_address, amount):
        nonce = w3_source.eth.get_transaction_count(warden_account_source.address)
        # Build the transaction to call the `withdraw` function
        tx = source_contract.functions.withdraw(token_address, recipient_address, amount).build_transaction({
            'chainId': 43113,
            'gas': 2000000,
            'gasPrice': w3_source.eth.gas_price,
            'nonce': nonce,
        })
        # Sign the transaction with the warden's private key
        signed_tx = w3_source.eth.account.sign_transaction(tx, private_key)
        # Send the signed transaction
        tx_hash = w3_source.eth.send_raw_transaction(signed_tx.rawTransaction)
        print(f"Transaction hash: {tx_hash.hex()}")

    if chain not in ['source', 'destination']:
        print(f"Invalid chain: {chain}")
        return

    if chain == 'source':
        contract_address = getContractInfo(chain)['address']
        contract = w3_source.eth.contract(address=contract_address, abi=source_contract_abi)

        arg_filter = {}
        end_block = w3_source.eth.get_block_number()
        start_block = end_block - 5
        print(f"Scanning blocks {start_block} - {end_block} on {chain}")
        event_filter = contract.events.Deposit.create_filter(fromBlock=start_block, toBlock=end_block,
                                                             argument_filters=arg_filter)
        events = event_filter.get_all_entries()
        for evt in events:
            print(evt.args['token'], evt.args['recipient'], evt.args['amount'])
            call_wrap_function(evt.args['token'], evt.args['recipient'], evt.args['amount'])

    elif chain == 'destination':
        contract_address = getContractInfo(chain)['address']
        contract = w3_destination.eth.contract(address=contract_address, abi=destination_contract_abi)

        arg_filter = {}
        end_block = w3_destination.eth.get_block_number()
        start_block = end_block - 5
        print(f"Scanning blocks {start_block} - {end_block} on {chain}")
        event_filter = contract.events.Unwrap.create_filter(fromBlock=start_block, toBlock=end_block,
                                                            argument_filters=arg_filter)
        events = event_filter.get_all_entries()
        for evt in events:
            print(evt.args['token'], evt.args['recipient'], evt.args['amount'])
            call_withdraw_function(evt.args['token'], evt.args['recipient'], evt.args['amount'])
