import requests
import json

def pin_to_ipfs(data):
	assert isinstance(data,dict), f"Error pin_to_ipfs expects a dictionary"
	#YOUR CODE HERE
	headers = {
        'pinata_api_key': PINATA_API_KEY,
        'pinata_secret_api_key': PINATA_API_SECRET
    }
    
	response = requests.post(PIN_JSON_TO_IPFS_URL, json=data, headers=headers)
    
	if response.status_code == 200:
		cid = response.json()['IpfsHash']
		return cid
	else:
		raise Exception(f"Failed to pin data to IPFS: {response.text}")


def get_from_ipfs(cid,content_type="json"):
	assert isinstance(cid,str), f"get_from_ipfs accepts a cid in the form of a string"
	#YOUR CODE HERE	

	assert isinstance(data,dict), f"get_from_ipfs should return a dict"
	response = requests.get(f"{GET_FROM_IPFS_URL}{cid}")
    
	if response.status_code == 200:
		if content_type == "json":
			data = response.json()
			assert isinstance(data, dict), f"get_from_ipfs should return a dict"
			return data
		else:
			raise Exception(f"Unsupported content type: {content_type}")
	else:
		raise Exception(f"Failed to retrieve data from IPFS: {response.text}")
