import time
import hmac
import hashlib
import requests

def _generate_signature(api_key, api_secret, data):
    # Urutkan parameter berdasarkan key untuk konsistensi
    sorted_items = sorted(data.items())
    post_data = "&".join([f"{key}={value}" for key, value in sorted_items])

    sign = hmac.new(api_secret.encode(), post_data.encode(), hashlib.sha512).hexdigest()
    headers = {
        "Key": api_key,
        "Sign": sign,
        "Content-Type": "application/x-www-form-urlencoded"  # ✅ Ini penting
    }
    return headers, post_data

def get_balance(api_key, api_secret):
    url = "https://indodax.com/tapi"
    nonce = int(time.time())
    data = {
        "method": "getInfo",
        "nonce": nonce
    }

    headers, post_data = _generate_signature(api_key, api_secret, data)
    response = requests.post(url, headers=headers, data=post_data)
    return response.json()

def place_buy_order(pair, amount_idr, api_key, api_secret):
    url = "https://indodax.com/tapi"
    nonce = int(time.time())

    data = {
        "method": "trade",
        "nonce": nonce,
        "pair": pair,
        "type": "buy",
        "price": 0,
        "idr": amount_idr
    }

    headers, post_data = _generate_signature(api_key, api_secret, data)
    response = requests.post(url, headers=headers, data=post_data)
    return response.json()

def place_grid_order(pair, price, amount, api_key, api_secret):
    url = "https://indodax.com/tapi"
    nonce = int(time.time())

    data = {
        "method": "trade",
        "nonce": nonce,
        "pair": pair,
        "type": "buy",
        "price": price,
        "idr": amount
    }

    headers, post_data = _generate_signature(api_key, api_secret, data)
    response = requests.post(url, headers=headers, data=post_data)
    return response.json()

def get_open_orders(api_key, api_secret):
    url = "https://indodax.com/tapi"
    nonce = int(time.time())

    data = {
        "method": "openOrders",
        "nonce": nonce
    }

    headers, post_data = _generate_signature(api_key, api_secret, data)
    response = requests.post(url, headers=headers, data=post_data)
    return response.json()
