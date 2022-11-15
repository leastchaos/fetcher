import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from src.exchange.database import get_data, get_key, get_redis

app = APIRouter(prefix="/ws", tags=["websockets"])


def parse_symbol(symbol: str) -> str:
    """parse symbol"""
    if symbol == "all":
        return "all"
    return symbol.replace("_", "/").replace("%3", ":")


@app.websocket("/balance/{account_name}/{asset}")
async def balance_ws(
    websocket: WebSocket, account_name: str = "all", asset: str = "all"
):
    """TODO: send updates only when there is a update in key value"""
    redis_client = get_redis()
    key = get_key("balance", account_name)
    asset = parse_symbol(asset)
    while True:
        try:
            data = get_data(redis_client, key)
            if account_name != "all":
                data = data[account_name]
                if asset != "all":
                    data = data[asset]
            await websocket.send_json(data)
            await asyncio.sleep(1)
        except WebSocketDisconnect:
            break
        except Exception as e:
            print(e)


@app.websocket("/open_orders/{account_name}/{symbol}")
async def open_orders_ws(
    websocket: WebSocket, account_name: str = "all", symbol: str = "all"
):
    """TODO: send updates only when there is a update in key value"""
    redis_client = get_redis()
    key = get_key("open_orders", account_name)
    symbol = parse_symbol(symbol)
    while True:
        try:
            data = get_data(redis_client, key)
            if account_name != "all":
                data = data[account_name]
                if symbol != "all":
                    data = data[symbol]
            await websocket.send_json(data)
            await asyncio.sleep(1)
        except WebSocketDisconnect:
            break
        except Exception as e:
            print(e)


@app.websocket("/positions/{account_name}/{symbol}")
async def positions_ws(websocket: WebSocket, account_name: str, symbol: str = "all"):
    """TODO: send updates only when there is a update in key value"""
    redis_client = get_redis()
    key = get_key("positions", account_name)
    symbol = parse_symbol(symbol)
    while True:
        try:
            data = get_data(redis_client, key)
            if symbol != "all":
                data = data[symbol]
            await websocket.send_json(data)
            await asyncio.sleep(1)
        except WebSocketDisconnect:
            break
        except Exception as e:
            print(e)
