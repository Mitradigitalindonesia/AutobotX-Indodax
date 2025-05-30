import time, hmac, hashlib, requests, threading, logging

BASE_URL = "https://indodax.com/tapi"
_lock = threading.Lock()
_last_nonce = int(time.time() * 1000)

def get_nonce():
    global _last_nonce
    with _lock:
        now = int(time.time() * 1000)
        _last_nonce = max(_last_nonce + 1, now)
        return _last_nonce

def _generate_signature(api_key, api_secret, data):
    post_data = "&".join([f"{key}={value}" for key, value in data.items()])
    sign = hmac.new(api_secret.encode(), post_data.encode(), hashlib.sha512).hexdigest()
    headers = {
        "Key": api_key,
        "Sign": sign
    }
    return headers, data

def safe_post(url, headers, data):
    try:
        response = requests.post(url, headers=headers, data=data, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Request error: {e}")
        return {"success": False, "error": str(e)}
    except ValueError:
        logging.error("Invalid JSON response from server.")
        return {"success": False, "error": "Invalid JSON response"}

def get_balance(api_key, api_secret):
    data = {
        "method": "getInfo",
        "nonce": get_nonce()
    }
    headers, post_data = _generate_signature(api_key, api_secret, data)
    return safe_post(BASE_URL, headers, post_data)

def place_buy_order(pair, amount_idr, api_key, api_secret):
    data = {
        "method": "trade",
        "nonce": get_nonce(),
        "pair": pair,
        "type": "buy",
        "price": 0,
        "idr": amount_idr
    }
    headers, post_data = _generate_signature(api_key, api_secret, data)
    return safe_post(BASE_URL, headers, post_data)

def place_grid_order(pair, price, amount, api_key, api_secret):
    data = {
        "method": "trade",
        "nonce": get_nonce(),
        "pair": pair,
        "type": "buy",
        "price": price,
        "idr": amount
    }
    headers, post_data = _generate_signature(api_key, api_secret, data)
    return safe_post(BASE_URL, headers, post_data)

def get_open_orders(api_key, api_secret):
    data = {
        "method": "openOrders",
        "nonce": get_nonce()
    }
    headers, post_data = _generate_signature(api_key, api_secret, data)
    return safe_post(BASE_URL, headers, post_data)
