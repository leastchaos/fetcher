"""fetch wallet data from ethplorer"""
import asyncio
import os
import time
from typing import Any

import aiohttp
import yaml
from fastapi import APIRouter
from pydantic import BaseModel

app = APIRouter(prefix="/wallet", tags=["wallet"])

BASE_URL = "https://api.covalenthq.com/v1/"
CREDENTIALS = os.path.join(os.path.dirname(__file__), "credentials.yml")


def get_config() -> dict[str, Any]:
    """returns the config"""
    with open(CREDENTIALS, "r", encoding="utf-8") as config_file:
        return yaml.safe_load(config_file)


API_KEY = get_config()["api_key"]


async def request(url: str, params: dict = None) -> dict:
    """request data from covalenthq"""
    if params is None:
        params = {}
    params.update({"key": API_KEY})
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            if response.status == 200:
                return await response.json()
    raise (Exception(f"Error: {response.status}: url: {url}"))


@app.get("/chains")
async def get_chains():
    """returns the chains available on cavalenthq"""
    url = f"{BASE_URL}chains/"
    params = {
        "quote-currency": "USD",
        "format": "JSON",
    }
    response = await request(url, params=params)
    return {data["label"]: data["chain_id"] for data in response["data"]["items"]}


@app.get("/balance/{address}/{chain_id}")
async def get_wallet_balance(chain_id: str, address: str):
    """returns the data for the address"""
    url = f"{BASE_URL}{chain_id}/address/{address}/balances_v2/"
    response = await request(url)
    return response["data"]


@app.get("/chain_balance/{account_name}")
async def get_wallet_chain_balance(account_name: str) -> dict[str, Any]:
    """returns the data for the address"""
    config = get_config()
    data = config["accounts"][account_name]
    address, chain_names = data["address"], data["chain_names"]
    chains = await get_chains()
    chain_ids = [chains[chain_name] for chain_name in chain_names]
    wallet_balances = await asyncio.gather(
        *[get_wallet_balance(chain_id, address) for chain_id in chain_ids]
    )
    return {
        chain_name: wallet for chain_name, wallet in zip(chain_names, wallet_balances)
    }


@app.get("/balances")
async def get_wallet_balances() -> dict[str, dict[str, Any]]:
    """main function"""
    config = get_config()
    chains = await get_chains()
    accounts: dict = config["accounts"]
    balances: dict = {}
    for account_name, data in accounts.items():
        balances[account_name] = {}
        address, chain_names = data["address"], data["chain_names"]
        for name in chain_names:
            chain_id = chains[name]
            balances[account_name][name] = await get_wallet_balance(chain_id, address)
            time.sleep(0.2)
    return balances


class WalletInfo(BaseModel):
    """define Wallet Info requirements"""

    account_name: str
    address: str
    chain_names: list[str]


# @app.post("/credential/")
# def add_credentials(info: WalletInfo) -> dict:
#     """add credentials to the config"""
#     config = get_config()
#     config["accounts"][info.account_name] = {
#         "address": info.address,
#         "chain_names": info.chain_names,
#     }
#     with open(CREDENTIALS, "w", encoding="utf-8") as config_file:
#         yaml.dump(config, config_file, default_flow_style=False)
#     return config["accounts"][info.account_name]


# @app.delete("/credential/{account_name}")
# def delete_credentials(account_name: str) -> dict:
#     """delete credentials from the config"""
#     config = get_config()
#     del config["accounts"][account_name]
#     with open(CREDENTIALS, "w", encoding="utf-8") as config_file:
#         yaml.dump(config, config_file, default_flow_style=False)
#     return config["accounts"][account_name]


if __name__ == "__main__":
    get_wallet_balances()
