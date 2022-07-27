"""get data from database with flask"""
import asyncio
import logging

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

from fetcher.database import get_data, get_key, get_redis

app = FastAPI()

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:8000/ws");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


@app.get("/")
async def get():
    return HTMLResponse(html)


@app.get("/balance/{account_name}")
def get_balance(account_name: str) -> dict[str, dict[str, float] | float]:
    """get balance"""
    redis_client = get_redis()
    key = get_key("balance", account_name)
    return get_data(redis_client, key)


@app.get("/loans/{account_name}")
def get_loans(account_name: str) -> dict[str, dict[str, float] | float]:
    """get loan"""
    redis_client = get_redis()
    key = get_key("loan", account_name)
    return get_data(redis_client, key)


@app.websocket("/ws")
async def websocket_balance(
    websocket: WebSocket, interval: float = 1
):  # , account_name: str):
    """get balance"""
    await websocket.accept()
    redis_client = get_redis()
    key = get_key("balance", "kucoin_main_main")
    prev_data = {}
    try:
        while True:
            data = get_data(redis_client, key)
            data.pop("timestamp", None)
            if data != prev_data:
                await websocket.send_json(data)
                prev_data = data
            await asyncio.sleep(interval)
    except WebSocketDisconnect:
        logging.info("Connection closed")
