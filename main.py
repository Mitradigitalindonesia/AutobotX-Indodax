from fastapi import FastAPI
from pydantic import BaseModel
from indodax_api import place_buy_order

app = FastAPI()

class BuyRequest(BaseModel):
    user_id: str
    pair: str
    amount: float  # Amount in IDR
    api_key: str   # User's Indodax API Key
    api_secret: str  # User's Indodax Secret Key

@app.get("/")
def root():
    return {"message": "Indodax Trading Bot API - Ready"}

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
