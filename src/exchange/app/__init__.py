"""get data from database with flask"""
from fastapi import APIRouter

from src.exchange.app.account_infos import app as account_infos_app
from src.exchange.app.open_orders import app as open_orders_app
from src.exchange.app.trade import app as trade_app

app = APIRouter(prefix="/exchange", tags=["exchange"])
app.include_router(account_infos_app)
app.include_router(open_orders_app)
app.include_router(trade_app)
