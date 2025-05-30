import os
import time
import hmac
import hashlib
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("INDODAX_API_KEY")
API_SECRET = os.getenv("INDODAX_API_SECRET")

def place_buy_order(pair: str, amount_idr: float):
    url = "https://indodax.com/tapi"
    method = "trade"
    nonce = int(time.time() * 1000)

    data = {
        "method": method,
        "nonce": nonce,
        "pair": pair,
        "type": "buy",
        "price": 0,           # Market order (set 0)
        "idr": amount_idr     # Amount in IDR
    }

    post_data = "&".join([f"{k}={v}" for k, v in data.items()])
    signature = hmac.new(API_SECRET.encode(), post_data.encode(), hashlib.sha512).hexdigest()

    headers = {
        "Key": API_KEY,
        "Sign": signature
    }

    response = requests.post(url, headers=headers, data=data)
    return response.json()
