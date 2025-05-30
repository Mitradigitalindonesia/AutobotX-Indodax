from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from database import Base

class TradeHistory(Base):
    __tablename__ = "trade_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String)
    pair = Column(String)
    amount = Column(Float)
    status = Column(String, default="pending")
    timestamp = Column(DateTime, default=datetime.utcnow)
