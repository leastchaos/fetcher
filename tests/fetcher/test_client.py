"""test client initialization"""
from fetcher.client import AccountInfo, get_client, get_clients


def test_get_client():
    """test client initialization"""
    account_info = AccountInfo(
        exchange_name="binance",
        api_key="api_key",
        secret="secret",
        password="password",
        uid="uid",
        default_type="spot",
        default_margin_mode="cross",
        options={},
    )
    client = get_client(account_info)
    assert client.apiKey == "api_key"
    assert client.secret == "secret"
    assert client.password == "password"
    assert client.uid == "uid"
    assert client.options["defaultType"] == "spot"
    assert client.options["defaultMarginMode"] == "cross"


def test_get_clients():
    """test client initialization"""
    clients = get_clients("./tests/data/test_credentials.yml")
    assert len(clients) == 2
