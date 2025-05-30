from fastapi import FastAPI
from pydantic import BaseModel
from indodax_api import place_buy_order
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

app = FastAPI()

# Mount folder static
app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve index.html UI
@app.get("/", response_class=FileResponse)
def serve_index():
    return FileResponse(os.path.join("static", "index.html"))
@app.post("/validate")
def validate_key(request: BuyRequest):
    try:
        balance = get_balance(api_key=request.api_key, api_secret=request.api_secret)
        if 'return' in balance:
            return {"success": True}
    except:
        pass
    return {"success": False}
# Request body model
class BuyRequest(BaseModel):
    user_id: str
    pair: str
    amount: float
    api_key: str
    api_secret: str

# Endpoint trade
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
