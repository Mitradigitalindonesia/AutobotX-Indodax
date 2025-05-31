import time
import hmac
import hashlib
import requests


def _generate_signature(api_key, api_secret, data):
    sorted_items = sorted(data.items())
    post_data = "&".join([f"{key}={value}" for key, value in sorted_items])

    sign = hmac.new(api_secret.encode(), post_data.encode(), hashlib.sha512).hexdigest()
    headers = {
        "Key": api_key,
        "Sign": sign,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    return headers, post_data


def get_balance(api_key, api_secret):
    url = "https://indodax.com/tapi"
    nonce = int(time.time() * 1000)
    data = {
        "method": "getInfo",
        "nonce": nonce
    }

    headers, post_data = _generate_signature(api_key, api_secret, data)
    response = requests.post(url, headers=headers, data=post_data)
    return response.json()


def place_buy_order(pair, amount_idr, api_key, api_secret):
    url = "https://indodax.com/tapi"
    nonce = int(time.time() * 1000)

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
    nonce = int(time.time() * 1000)

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
    nonce = int(time.time() * 1000)

    data = {
        "method": "openOrders",
        "nonce": nonce
    }

    headers, post_data = _generate_signature(api_key, api_secret, data)
    response = requests.post(url, headers=headers, data=post_data)
    return response.json()


def get_portfolio_valuation(api_key, api_secret):
    """
    Mengembalikan portofolio user berupa daftar aset yang dimiliki
    beserta saldo, harga saat ini, dan nilai total (value).
    """
    balance_data = get_balance(api_key, api_secret)
    if balance_data.get("success") != 1:
        return {"success": False, "error": balance_data.get("error", "Gagal ambil saldo.")}

    balances = balance_data["return"]["balance"]
    result = []

    for asset, amount in balances.items():
        amount = float(amount)
        if amount == 0 or asset == "idr":
            continue

        pair = f"{asset}_idr"
        ticker_url = f"https://indodax.com/api/{pair}/ticker"

        try:
            ticker_res = requests.get(ticker_url, timeout=5)
            ticker_json = ticker_res.json()
            price = float(ticker_json["ticker"]["last"])
            value = amount * price

            result.append({
                "asset": asset,
                "balance": amount,
                "price": price,
                "value": value
            })
        except Exception:
            continue  # Lewati aset jika gagal mengambil harga

    # Tambahkan IDR sebagai aset
    idr_balance = float(balances.get("idr", 0))
    result.append({
        "asset": "idr",
        "balance": idr_balance,
        "price": 1,
        "value": idr_balance
    })

    return {"success": True, "portfolio": result}
