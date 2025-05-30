# Indodax Trading Bot (FastAPI)

API sederhana untuk melakukan trading crypto melalui Indodax API, menggunakan akun master.

## Fitur
- 🛒 Buy order crypto (Market)
- 🔐 API key disimpan aman di `.env`
- 🚀 Siap deploy ke Render.com

## Setup Lokal

```bash
git clone https://github.com/yourname/indodax-trading-bot.git
cd indodax-trading-bot
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Masukkan API key di .env
uvicorn main:app --reload
