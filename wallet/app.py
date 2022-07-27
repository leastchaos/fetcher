"""fetch wallet data from ethplorer"""
import logging
import os
import time
from typing import Any

import requests
import yaml
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

BASE_URL = "https://api.covalenthq.com/v1/"
CREDENTIALS = os.path.join(os.path.dirname(__file__), "credentials.yml")


def get_config() -> dict[str, Any]:
    """returns the config"""
    with open(CREDENTIALS, "r", encoding="utf-8") as config_file:
        return yaml.safe_load(config_file)


API_KEY = get_config()["api_key"]


@app.get("/chains")
def get_chains():
    """returns the chains available on cavalenthq"""
    url = f"{BASE_URL}chains/"
    params = {
        "quote-currency": "USD",
        "format": "JSON",
        "key": API_KEY,
    }
    try:
        response = requests.get(url, params).json()
    except requests.exceptions.RequestException as err:
        logging.error(err)
        return None
    return {data["label"]: data["chain_id"] for data in response["data"]["items"]}


@app.get("/wallet/{address}/{chain_id}")
def get_wallet_balance(chain_id: str, address: str):
    """returns the data for the address"""
    url = f"{BASE_URL}{chain_id}/address/{address}/balances_v2/"
    params = {"key": API_KEY}
    response = requests.get(url, params=params)
    if response.status_code != 200:
        logging.error("requests: %s failed: %s", response.url, response)
        return None
    return response.json()


@app.get("/wallet/{account_name}")
def get_wallet_chain_balance(account_name: str) -> dict[str, Any]:
    """returns the data for the address"""
    config = get_config()
    data = config["accounts"][account_name]
    address, chain_names = data["address"], data["chain_names"]
    chains = get_chains()
    chain_ids = [chains[chain_name] for chain_name in chain_names]
    return {
        chain_name: get_wallet_balance(chain_id, address)
        for chain_name, chain_id in zip(chain_names, chain_ids)
    }


@app.get("/wallets")
def get_wallet_balances() -> dict[str, dict[str, Any]]:
    """main function"""
    config = get_config()
    chains = get_chains()
    api_key = config["api_key"]
    accounts: dict = config["accounts"]
    balances: dict = {}
    for account_name, data in accounts.items():
        balances[account_name] = {}
        address, chain_names = data["address"], data["chain_names"]
        for name in chain_names:
            chain_id = chains[name]
            balances[account_name][name] = get_wallet_balance(
                chain_id, address, api_key
            )
            time.sleep(0.2)


class WalletInfo(BaseModel):
    """define Wallet Info requirements"""

    account_name: str
    address: str
    chain_names: list[str]


@app.post("/wallet/")
def add_credentials(info: WalletInfo) -> dict:
    """add credentials to the config"""
    config = get_config()
    config["accounts"][info.account_name] = {
        "address": info.address,
        "chain_names": info.chain_names,
    }
    with open(CREDENTIALS, "w", encoding="utf-8") as config_file:
        yaml.dump(config, config_file, default_flow_style=False)
    return config["accounts"][info.account_name]


@app.delete("/wallet/{account_name}")
def delete_credentials(account_name: str) -> dict:
    """delete credentials from the config"""
    config = get_config()
    del config["accounts"][account_name]
    with open(CREDENTIALS, "w", encoding="utf-8") as config_file:
        yaml.dump(config, config_file, default_flow_style=False)
    return config["accounts"][account_name]


if __name__ == "__main__":
    get_wallet_balances()
