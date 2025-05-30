from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os

from indodax_api import place_buy_order, get_balance, place_grid_order

app = FastAPI()

# Mount static folder
app.mount("/static", StaticFiles(directory="static"), name="static")

# Models
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

# Serve UI
@app.get("/", response_class=FileResponse)
def serve_index():
    return FileResponse(os.path.join("static", "index.html"))

# Validate API key
@app.post("/validate")
def validate_key(request: ValidateRequest):
    try:
        balance = get_balance(api_key=request.api_key, api_secret=request.api_secret)
        if 'return' in balance:
            return {"success": True}
    except:
        pass
    return {"success": False}

# Buy order
@app.post("/trade/buy")
def trade_buy(request: BuyRequest):
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

# Get portfolio
@app.post("/portfolio")
def get_portfolio(request: PortfolioRequest):
    balance = get_balance(api_key=request.api_key, api_secret=request.api_secret)
    if 'return' in balance:
        return {"success": True, "return": balance}
    return {"success": False, "message": "Failed to fetch portfolio"}

# Start grid bot (demo version)
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
        return {"message": f"Error: {str(e)}"}
