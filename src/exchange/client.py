"""define the expected input to generate ccxt exchange class"""
import logging
import os
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, Field

try:
    import ccxtpro as ccxt
except ImportError:
    import ccxt.async_support as ccxt

AllowedType = Literal["main", "trade", "spot", "margin", "future", "swap"]
CREDENTIALS = os.path.join(os.path.dirname(__file__), "credentials/credentials.yml")


class AccountInfo(BaseModel):
    """define the expected input to generate ccxt exchange class"""

    exchange_name: str
    api_key: str
    secret: str | None
    password: str | None
    uid: str | None
    default_type: AllowedType = "spot"
    default_margin_mode: Literal["cross", "isolated"] | None = None
    options: dict = Field(default_factory=dict)


def get_client(account: AccountInfo, name: str = None) -> ccxt.Exchange:
    """get the exchange class"""
    account.options["defaultType"] = account.default_type
    account.options["defaultMarginMode"] = account.default_margin_mode
    account.options["name"] = name if name else account.exchange_name
    return getattr(ccxt, account.exchange_name)(
        {
            "apiKey": account.api_key,
            "secret": account.secret,
            "password": account.password,
            "uid": account.uid,
            "options": account.options,
        }
    )


def get_clients(credentials: str = CREDENTIALS) -> dict[str, ccxt.Exchange]:
    """get the exchange classes"""
    credentials_path = Path(credentials)
    if not credentials_path.exists():
        raise FileNotFoundError(f"{credentials} not found")
    try:
        with credentials_path.open(encoding="utf-8") as file:
            credentials: dict[str, dict[str, Any]] = yaml.full_load(file)
    except yaml.YAMLError as err:
        logging.error("%s is not a valid file", err)
        raise
    return {
        account_name: get_client(AccountInfo.parse_obj(account_info), account_name)
        for account_name, account_info in credentials.items()
    }
