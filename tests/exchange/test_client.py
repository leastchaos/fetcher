"""test client initialization"""
import asyncio

import pytest

from exchange.client import AccountInfo, get_client, get_clients


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


@pytest.mark.slow
async def test_client_credentials():
    """test actual clients"""
    clients = get_clients()

    async def load_markets(client) -> None:
        try:
            await client.fetch_balance()
        except Exception as err:  # pylint: disable=broad-except
            await client.close()
            return err
        await client.close()
        return True

    results = await asyncio.gather(
        *[load_markets(client) for client in clients.values()]
    )
    failed = [
        f"{account_name}: {result}"
        for account_name, result in zip(clients.keys(), results)
        if result is not True
    ]
    if failed:
        pytest.fail("\n".join(failed))
