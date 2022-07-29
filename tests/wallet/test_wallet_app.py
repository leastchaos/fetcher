"""test exchange app"""
import os

from fastapi.testclient import TestClient

from src.wallet.app import app
from tests.utils import load_yml

client = TestClient(app)
credentials = load_yml(
    os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "src/wallet/credentials.yml",
    )
)
test_account, test_wallet = list(credentials["accounts"].items())[0]


def test_get_chains():
    """test get chains"""
    response = client.get("/wallet/chains")
    data = response.json()
    assert response.status_code == 200
    assert data["Ethereum Mainnet"] == "1"


def test_get_wallet_balance():
    """test get wallet balance"""
    response = client.get(f"/wallet/balance/{test_wallet['address']}/1")
    assert response.status_code == 200
    data = response.json()
    assert data


def test_get_wallet_chain_balance():
    """test get wallet chain balance"""
    response = client.get(f"/wallet/chain_balance/{test_account}")
    assert response.status_code == 200
    assert response.json()


def test_get_wallet_balances():
    """test get wallet balances"""
    response = client.get("/wallet/balances")
    assert response.status_code == 200
    data = response.json()
    for account_name in credentials["accounts"]:
        assert account_name in data
