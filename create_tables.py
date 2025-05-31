# create_tables.py
from database import engine, Base
from models import TradeHistory, PortfolioSnapshot

# Membuat semua tabel dari model
Base.metadata.create_all(bind=engine)
print("✅ Semua tabel berhasil dibuat.")
