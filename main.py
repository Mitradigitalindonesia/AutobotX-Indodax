from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import os

from indodax_api import place_buy_order, get_balance, place_grid_order

app = FastAPI()

# Mount static and template directories
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# In-memory store for active grid orders (simple simulation)
active_orders = []

# === Request Models ===
class BuyRequest(BaseModel):
    user_id: str
    pair: str
    amount: float
    api_key: str
    api_secret: str

class ValidateRequest(BaseModel):
    api_key: str
    api_secret: str

class PortfolioRequest(BaseModel):
    api_key: str
    api_secret: str

class StartBotRequest(BaseModel):
    api_key: str
    api_secret: str
    pair: str
    min_price: float
    max_price: float
    grid_size: int
    budget: float

class GridTradingRequest(BaseModel):
    pair: str
    low_price: float
    high_price: float
    grid_count: int
    balance: float

# === UI Routes ===

@app.get("/", response_class=FileResponse)
def serve_index():
    return FileResponse(os.path.join("static", "index.html"))

@app.get("/dashboard", response_class=HTMLResponse)
def get_dashboard(request: Request):
    # Dummy portfolio (replace with real user balance or session data if implemented)
    portfolio = {"idr": 5000000, "btc": 0.01}
    pairs = ["btc_idr", "eth_idr", "bnb_idr"]
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "portfolio": portfolio,
        "pairs": pairs
    })

# === API Endpoints ===

@app.post("/validate")
def validate_key(request: ValidateRequest):
    try:
        balance = get_balance(api_key=request.api_key, api_secret=request.api_secret)
        if 'return' in balance:
            return {"success": True}
    except Exception as e:
        print("❌ Error during validation:", str(e))
    return {"success": False}

@app.post("/trade/buy")
def trade_buy(request: BuyRequest):
    try:
        result = place_buy_order(
            pair=request.pair,
            amount_idr=request.amount,
            api_key=request.api_key,
            api_secret=request.api_secret
        )
        return {
            "user_id": request.user_id,
            "pair": request.pair,
            "amount": request.amount,
            "result": result
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/portfolio")
def get_portfolio(request: PortfolioRequest):
    try:
        balance = get_balance(api_key=request.api_key, api_secret=request.api_secret)
        if 'return' in balance and 'balance' in balance['return']:
            return {"success": True, "return": balance['return']}
        return {"success": False, "raw": balance}
    except Exception as e:
        return {"success": False, "message": "Failed to fetch portfolio", "error": str(e)}

@app.post("/start-bot")
def start_bot(req: StartBotRequest):
    try:
        price_step = (req.max_price - req.min_price) / req.grid_size
        actions = []

        for i in range(req.grid_size):
            price = req.min_price + i * price_step
            result = place_grid_order(
                pair=req.pair,
                price=price,
                amount=req.budget,
                api_key=req.api_key,
                api_secret=req.api_secret
            )
            actions.append(result)

        return {"message": "Grid bot started", "orders": actions}
    except Exception as e:
        return {"message": "Error starting grid bot", "error": str(e)}

# === Grid Trading via Dashboard ===

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

        # Cek saldo terlebih dahulu
        user_balance = get_balance(api_key=api_key, api_secret=api_secret)
        idr_balance = float(user_balance['return']['balance']['idr'])

        if idr_balance < balance:
            return JSONResponse(status_code=400, content={"success": False, "message": "Saldo IDR tidak mencukupi"})

        # Kirim order nyata per grid
        orders = []
        for i in range(grid_count):
            price = low_price + i * price_step
            result = place_grid_order(
                pair=pair,
                price=round(price, 2),
                amount=amount_per_order,
                api_key=api_key,
                api_secret=api_secret
            )
            orders.append(result)

        return {"success": True, "message": "Grid orders placed", "orders": orders}

    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})
@app.get("/positions")
def get_positions():
    return active_orders
