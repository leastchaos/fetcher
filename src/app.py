"""main application"""
import yaml
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from .exchange.app import app as exchange_app
from .wallet.app import app as wallet_app

app = FastAPI(title="fetcher")
app.include_router(exchange_app)
app.include_router(wallet_app)
try:
    from src.hb_app.app import app as hb_app

    app.include_router(hb_app)
except ImportError:
    pass


@app.get("/")
def get_root():
    """get root"""
    return RedirectResponse("/docs")


@app.on_event("startup")
async def startup():
    """startup"""
    with open("./fetcher_sdk/openapi.yml", "w+") as f:
        yaml.dump(app.openapi(), f)
