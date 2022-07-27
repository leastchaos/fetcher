"""main application"""
from fastapi import FastAPI

from .exchange.app import app as exchange_app
from .wallet.app import app as wallet_app

app = FastAPI()
app.include_router(exchange_app)
app.include_router(wallet_app)


@app.get("/")
def get_root():
    """get root"""
    return {"message": "Hello World"}
