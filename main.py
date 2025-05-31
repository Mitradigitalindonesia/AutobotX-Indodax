from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import os, logging, requests
from indodax_api import place_buy_order, get_balance, place_grid_order, get_open_orders

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

logging.basicConfig(level=logging.INFO, force=True)

# --------------------- Models ---------------------
class GridTradingRequest(BaseModel):
    pair: str
    low_price: float
    high_price: float
    grid_count: int
    balance: float
    api_key: str
    api_secret: str

class PositionsRequest(BaseModel):
    api_key: str
    api_secret: str

class ValidateRequest(BaseModel):
    api_key: str
    api_secret: str

class PortfolioRequest(BaseModel):
    api_key: str
    api_secret: str

# --------------------- Routes ---------------------
@app.get("/", response_class=FileResponse)
def serve_index():
    return FileResponse(os.path.join("static", "index.html"))

@app.head("/")
def health_check():
    return JSONResponse(content=None)

@app.get("/dashboard", response_class=HTMLResponse)
def get_dashboard(request: Request):
    portfolio = {"idr": 0, "btc": 0}
    pairs = ["btc_idr", "eth_idr", "bnb_idr"]
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "portfolio": portfolio,
        "pairs": pairs
    })

@app.post("/validate")
async def validate(request: ValidateRequest):
    try:
        result = get_balance(request.api_key, request.api_secret)
        logging.info(f"Indodax validate response: {result}")
        if result.get("success") == 1:
            return {"success": True}
        return {"success": False, "error": result.get("error", "Gagal autentikasi.")}
    except Exception as e:
        logging.exception("Validasi gagal")
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@app.post("/portfolio")
def get_portfolio(data: PortfolioRequest):
    try:
        info = get_balance(data.api_key, data.api_secret)
        balances = info.get("return", {}).get("balance", {})

        # Ambil harga pasar saat ini
        prices_response = requests.get("https://indodax.com/api/summaries")
        prices_data = prices_response.json().get("tickers", {})

        portfolio = []
        total_value = 0.0

        for asset, amount_str in balances.items():
            amount = float(amount_str)
            if amount <= 0:
                continue

            market_key = f"{asset.lower()}_idr"
            price = float(prices_data.get(market_key, {}).get("last", 0))

            if price == 0:
                continue  # Lewati aset yang tidak ada pasangan IDR-nya

            value = amount * price
            portfolio.append({
                "asset": asset.upper(),
                "amount": amount,
                "price": price,
                "value": value
            })
            total_value += value

        return {
            "success": True,
            "portfolio": portfolio,
            "total_value": total_value
        }

    except Exception as e:
        logging.exception("Gagal ambil portfolio")
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@app.post("/positions")
def get_positions(request: PositionsRequest):
    try:
        orders = get_open_orders(api_key=request.api_key, api_secret=request.api_secret)
        return {"success": True, "orders": orders}
    except Exception as e:
        logging.exception("Failed to get positions")
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@app.post("/start_grid_trading")
async def start_grid_trading(request: Request):
    try:
        data = await request.json()
        pair = data["pair"]
        low_price = float(data["low_price"])
        high_price = float(data["high_price"])
        grid_count = int(data["grid_count"])
        balance = float(data["balance"])
        api_key = data["api_key"]
        api_secret = data["api_secret"]

        price_step = (high_price - low_price) / grid_count
        amount_per_order = balance / grid_count

        user_balance = get_balance(api_key, api_secret)
        idr_balance = float(user_balance.get("return", {}).get("balance", {}).get("idr", 0))

        if idr_balance < balance:
            return JSONResponse(status_code=400, content={"success": False, "message": "Saldo IDR tidak cukup."})

        orders = []
        for i in range(grid_count):
            price = round(low_price + i * price_step, 2)
            result = place_grid_order(pair, price, amount_per_order, api_key, api_secret)
            orders.append(result)

        return {"success": True, "message": "Grid orders placed", "orders": orders}

    except Exception as e:
        logging.exception("Grid trading failed")
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})
