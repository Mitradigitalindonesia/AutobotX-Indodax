from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import SessionLocal
from indodax_api import place_buy_order
from models import TradeHistory
from datetime import datetime

app = FastAPI()

class BuyRequest(BaseModel):
    user_id: str
    pair: str
    amount: float

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/trade/buy")
def trade_buy(request: BuyRequest, db: Session = Depends(get_db)):
    # Simpan transaksi ke database
    new_trade = TradeHistory(
        user_id=request.user_id,
        pair=request.pair,
        amount=request.amount,
        status="pending",
        timestamp=datetime.utcnow()
    )
    db.add(new_trade)
    db.commit()
    db.refresh(new_trade)

    # Kirim order ke Indodax
    result = place_buy_order(request.pair, request.amount)

    # Update status transaksi
    new_trade.status = "success" if result.get("success") == 1 else "failed"
    db.commit()

    return {"message": "Buy order processed", "order_id": new_trade.id, "indodax_result": result}
