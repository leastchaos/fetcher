import asyncio

from src.exchange.component.client import get_clients


async def main():
    clients = get_clients()
    client = clients["kucoin_main_spot"]
    orders = await client.fetch_open_orders()
    orders = {order["symbol"]: {order["id"]: order} for order in orders}
    while True:
        update = await client.watch_orders()
        for order in update:
            if order["symbol"] not in orders:
                orders[order["symbol"]] = {}
            if order["status"] == "open":
                orders[order["symbol"]][order["id"]] = order
            else:
                orders[order["symbol"]].pop(order["id"], None)


if __name__ == "__main__":
    asyncio.run(main())
