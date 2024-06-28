import requests
import json

# Pinata JWT token
PINATA_JWT = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySW5mb3JtYXRpb24iOnsiaWQiOiIzOTU5Yzc1Ny0wNGQ0LTRjYWYtODllNi05ZjkzZGNkMGRhNjAiLCJlbWFpbCI6InFjaGVuOTJAZm9yZGhhbS5lZHUiLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwicGluX3BvbGljeSI6eyJyZWdpb25zIjpbeyJpZCI6IkZSQTEiLCJkZXNpcmVkUmVwbGljYXRpb25Db3VudCI6MX0seyJpZCI6Ik5ZQzEiLCJkZXNpcmVkUmVwbGljYXRpb25Db3VudCI6MX1dLCJ2ZXJzaW9uIjoxfSwibWZhX2VuYWJsZWQiOmZhbHNlLCJzdGF0dXMiOiJBQ1RJVkUifSwiYXV0aGVudGljYXRpb25UeXBlIjoic2NvcGVkS2V5Iiwic2NvcGVkS2V5S2V5IjoiNGRkNzJiN2IwMmVjMDRjYTZjNjQiLCJzY29wZWRLZXlTZWNyZXQiOiI3NmUyODM1Y2FhYjY4MWJlYjY3Y2I4ZTIyMWY2ODU5NWNiOTcwYTZlYWExZDRjMDI3MjEwZWViOTY0NTMzYWI2IiwiaWF0IjoxNzE5NTM5MzUxfQ.5XK-vX02DOkDkfDjOTwMzIGOIGQoZfXVxq18NANmpK0'

# Pinata URLs
PINATA_BASE_URL = 'https://api.pinata.cloud'
PIN_JSON_TO_IPFS_URL = f"{PINATA_BASE_URL}/pinning/pinJSONToIPFS"
GET_FROM_IPFS_URL = 'https://gateway.pinata.cloud/ipfs/'

def pin_to_ipfs(data):
    assert isinstance(data, dict), f"Error pin_to_ipfs expects a dictionary"
    
    headers = {
        'Authorization': f'Bearer {PINATA_JWT}',
        'Content-Type': 'application/json'
    }
    
    response = requests.post(PIN_JSON_TO_IPFS_URL, json=data, headers=headers)
    
    if response.status_code == 200:
        cid = response.json()['IpfsHash']
        return cid
    else:
        raise Exception(f"Failed to pin data to IPFS: {response.text}")

def get_from_ipfs(cid, content_type="json"):
    assert isinstance(cid, str), f"get_from_ipfs accepts a cid in the form of a string"
    
    response = requests.get(f"{GET_FROM_IPFS_URL}{cid}")
    
    if response.status_code == 200:
        if content_type == "json":
            try:
                data = response.json()
                assert isinstance(data, dict), f"get_from_ipfs should return a dict"
                return data
            except json.JSONDecodeError:
                raise Exception(f"Failed to decode JSON content from IPFS: {response.text}")
        else:
            raise Exception(f"Unsupported content type: {content_type}")
    else:
        raise Exception(f"Failed to retrieve data from IPFS: {response.text}")
