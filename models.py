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

class UserPortfolio(Base):
    __tablename__ = "user_portfolios"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True)
    initial_value = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
