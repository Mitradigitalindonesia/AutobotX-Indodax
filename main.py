from fastapi import FastAPI
from pydantic import BaseModel
from indodax_api import place_buy_order

app = FastAPI()

class BuyRequest(BaseModel):
    user_id: str
    pair: str
    amount: float  # Amount in IDR

@app.get("/")
def root():
    return {"message": "Indodax Trading Bot API"}

@app.post("/trade/buy")
def trade_buy(request: BuyRequest):
    result = place_buy_order(request.pair, request.amount)
    return {"message": "Buy order placed", "result": result}
