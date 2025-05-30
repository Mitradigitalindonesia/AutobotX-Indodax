import time
import hmac
import hashlib
import requests

def get_balance(api_key, api_secret):
    url = "https://indodax.com/tapi"
    method = "getInfo"
    nonce = int(time.time() * 1000)

    data = {
        "method": method,
        "nonce": nonce
    }

    post_data = "&".join([f"{k}={v}" for k, v in data.items()])
    signature = hmac.new(api_secret.encode(), post_data.encode(), hashlib.sha512).hexdigest()

    headers = {
        "Key": api_key,
        "Sign": signature
    }

    response = requests.post(url, headers=headers, data=data)
    return response.json()
