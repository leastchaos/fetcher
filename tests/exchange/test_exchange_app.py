"""test exchange app"""
import os

import yaml
from fastapi.testclient import TestClient

from src.exchange.app import app
from src.exchange.models.balance import AccountInfo, Balance
from src.exchange.models.ticker import Ticker

client = TestClient(app)


def load_yml(file_name) -> dict[str, dict[str, float | str]]:
    with open(file_name, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


cred_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "src/exchange/credentials/credentials.yml",
)
credentials = load_yml(cred_path)


def test_get_balances():
    response = client.get("/exchange/balances")
    assert response.status_code == 200
    account_names = list(credentials.keys())
    response_data = response.json()
    assert set(response_data.keys()) == set(account_names)


def test_get_loans():
    response = client.get("/exchange/loans")
    assert response.status_code == 200
    account_names = [
        name
        for name, data in credentials.items()
        if data.get("default_type") == "margin" or data.get("default_margin_mode")
    ]
    response_data = response.json()
    assert set(response_data.keys()) == set(account_names)


def test_get_balance():
    for account_name in credentials:
        response = client.get(f"/exchange/balance/{account_name}")
        assert response.status_code == 200
        assert Balance(**response.json())


def test_get_loan():
    for account_name in credentials:
        response = client.get(f"/exchange/loan/{account_name}")
        assert response.status_code == 200


def test_get_tickers():
    response = client.get("/exchange/tickers")
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_get_ticker():
    response = client.get("/exchange/ticker/kucoin_main_spot/BTC_USDT")
    assert response.status_code == 200
    assert Ticker(**response.json())


def test_get_account_infos():
    response = client.get("/exchange/account_infos")
    assert response.status_code == 200
    response_json = response.json()
    account_names = list(credentials.keys())
    assert set(response_json.keys()) == set(account_names)
    for account_name, data in response_json.items():
        assert AccountInfo(**data)
