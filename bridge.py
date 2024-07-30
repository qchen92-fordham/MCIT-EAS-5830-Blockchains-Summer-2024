from web3 import Web3
from web3.contract import Contract
from web3.providers.rpc import HTTPProvider
from web3.middleware import geth_poa_middleware #Necessary for POA chains
import json
import sys
from pathlib import Path

source_chain = 'avax'
destination_chain = 'bsc'
contract_info = "contract_info.json"

def connectTo(chain):
    if chain == 'avax':
        api_url = f"https://api.avax-test.network/ext/bc/C/rpc" #AVAX C-chain testnet

    if chain == 'bsc':
        api_url = f"https://data-seed-prebsc-1-s1.binance.org:8545/" #BSC testnet

    if chain in ['avax','bsc']:
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
        with p.open('r')  as f:
            contracts = json.load(f)
    except Exception as e:
        print( "Failed to read contract info" )
        print( "Please contact your instructor" )
        print( e )
        sys.exit(1)

    return contracts[chain]


warden_address = '0x3b7f6e8011Bc2137ea1Aca77fAeDbe84Af46374A'
warden_private_key = 'b3d8146f623407e7691479caeefb6332b60665ad9fee90a8697feaac79b783b0'



def scanBlocks(chain):
    """
        chain - (string) should be either "source" or "destination"
        Scan the last 5 blocks of the source and destination chains
        Look for 'Deposit' events on the source chain and 'Unwrap' events on the destination chain
        When Deposit events are found on the source chain, call the 'wrap' function the destination chain
        When Unwrap events are found on the destination chain, call the 'withdraw' function on the source chain
    """

    if chain not in ['source','destination']:
        print( f"Invalid chain: {chain}" )
        return
    
    #YOUR CODE HERE
    src_web3 = connectTo(source_chain)
    dest_web3 = connectTo(destination_chain)

    src_contract_info = getContractInfo(source_chain)
    dest_contract_info = getContractInfo(destination_chain)

    src_contract = src_web3.eth.contract(address=src_contract_info['address'], abi=src_contract_info['abi'])
    dest_contract = dest_web3.eth.contract(address=dest_contract_info['address'], abi=dest_contract_info['abi'])

    if chain == 'source':
        web3 = src_web3
        event_name = 'Deposit'
        other_contract = dest_contract
        other_web3 = dest_web3
        function_name = 'wrap'
    elif chain == 'destination':
        web3 = dest_web3
        event_name = 'Unwrap'
        other_contract = src_contract
        other_web3 = src_web3
        function_name = 'withdraw'

    end_block = web3.eth.blockNumber
    start_block = end_block - 5

    event_filter = getattr(src_contract.events, event_name).createFilter(fromBlock=start_block, toBlock=end_block)
    events = event_filter.get_all_entries()

    for event in events:
        if event_name == 'Deposit':
            token = event['args']['token']
            recipient = event['args']['recipient']
            amount = event['args']['amount']
        elif event_name == 'Unwrap':
            token = event['args']['underlying_token']
            recipient = event['args']['to']
            amount = event['args']['amount']

        transaction = getattr(other_contract.functions, function_name)(token, recipient, amount).buildTransaction({
            'from': warden_address,
            'nonce': other_web3.eth.getTransactionCount(warden_address),
            'gas': 5000000,
            'gasPrice': other_web3.toWei('50', 'gwei')
        })
        signed_tx = other_web3.eth.account.signTransaction(transaction, warden_private_key)
        tx_hash = other_web3.eth.sendRawTransaction(signed_tx.rawTransaction)
        other_web3.eth.waitForTransactionReceipt(tx_hash)
        print(f"Transaction {function_name} sent: {tx_hash.hex()}")
