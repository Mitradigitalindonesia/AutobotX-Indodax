import time
import hmac
import hashlib
import requests

def place_buy_order(pair: str, amount_idr: float, api_key: str, api_secret: str):
    url = "https://indodax.com/tapi"
    method = "trade"
    nonce = int(time.time() * 1000)

    data = {
        "method": method,
        "nonce": nonce,
        "pair": pair,
        "type": "buy",
        "price": 0,
        "idr": amount_idr
    }

    post_data = "&".join([f"{k}={v}" for k, v in data.items()])
    signature = hmac.new(api_secret.encode(), post_data.encode(), hashlib.sha512).hexdigest()

    headers = {
        "Key": api_key,
        "Sign": signature
    }

    response = requests.post(url, headers=headers, data=data)
    return response.json()
