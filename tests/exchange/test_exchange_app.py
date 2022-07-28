"""test exchange app"""
import os

import yaml
from fastapi.testclient import TestClient

from src.exchange.app import app

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
        assert response.json()["timestamp"] is not None


def test_get_loan():
    for account_name in credentials:
        response = client.get(f"/exchange/loan/{account_name}")
        assert response.status_code == 200
