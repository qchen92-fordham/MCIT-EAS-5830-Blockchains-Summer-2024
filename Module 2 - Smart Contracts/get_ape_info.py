from web3 import Web3
from web3.contract import Contract
from web3.providers.rpc import HTTPProvider
import requests
import json
import time

bayc_address = "0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D"
contract_address = Web3.to_checksum_address(bayc_address)

#You will need the ABI to connect to the contract
#The file 'abi.json' has the ABI for the bored ape contract
#In general, you can get contract ABIs from etherscan
#https://api.etherscan.io/api?module=contract&action=getabi&address=0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D
with open('/home/codio/workspace/abi.json', 'r') as f:
	abi = json.load(f) 

############################
#Connect to an Ethereum node
api_url = "https://mainnet.infura.io/v3/55313acc19f041af8e48d88062d3d574"
provider = HTTPProvider(api_url)
web3 = Web3(provider)

def get_ape_info(apeID):
	assert isinstance(apeID,int), f"{apeID} is not an int"
	assert 1 <= apeID, f"{apeID} must be at least 1"

	# Connect to the contract
	contract = web3.eth.contract(address=contract_address, abi=abi)

	data = {'owner': "", 'image': "", 'eyes': "" }
	
	# Fetch the owner of the ape
	owner = contract.functions.ownerOf(apeID).call()
	data['owner'] = owner

	# Get the token URI which contains the metadata
	token_uri = contract.functions.tokenURI(apeID).call()

	# Convert IPFS URI to HTTP URL if necessary
	ipfs_gateway = "https://ipfs.io/ipfs/"
	ipfs_hash = token_uri.replace("ipfs://", "")
	metadata_url = ipfs_gateway + ipfs_hash

	# Fetch the metadata from the token URI
	response = requests.get(metadata_url)
	response.raise_for_status()  # Ensure the request was successful
	metadata = response.json()

	# Extract the image URL
	data['image'] = metadata["image"]

	# Extract the 'eyes' attribute from the metadata
	for attribute in metadata.get("attributes", []):
		if attribute.get("trait_type", "").lower() == "eyes":
			data['eyes'] = attribute.get("value", "")
			break

	assert isinstance(data,dict), f'get_ape_info{apeID} should return a dict' 
	assert all( [a in data.keys() for a in ['owner','image','eyes']] ), f"return value should include the keys 'owner','image' and 'eyes'"
	return data

