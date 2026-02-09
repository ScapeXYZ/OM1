"""
Test cases for WalletCoinbase input plugin.
"""

import os
from unittest.mock import MagicMock, patch

import pytest

from inputs.plugins.wallet_coinbase import (
    Message,
    WalletCoinbase,
    WalletCoinbaseConfig,
)


def test_initialization_missing_wallet_id_and_missing_keys():
    """Missing wallet ID and API keys should result in no wallet."""
    with patch.dict(os.environ, {}, clear=True):
        wallet = WalletCoinbase(config=WalletCoinbaseConfig())

        assert wallet.wallet is None
        assert wallet.balance == 0.0
        assert wallet.balance_previous == 0.0


def test_initialization_creates_wallet_when_keys_present_but_id_missing():
    """Missing wallet ID but valid API keys should auto-create a wallet."""
    mock_wallet = MagicMock()
    mock_wallet.id = "new_wallet_id"
    mock_wallet.balance.return_value = "0.0"

    env = {
        "COINBASE_API_KEY": "k",
        "COINBASE_API_SECRET": "s",
    }

    with (
        patch.dict(os.environ, env, clear=True),
        patch("inputs.plugins.wallet_coinbase.Cdp.configure") as mock_configure,
        patch(
            "inputs.plugins.wallet_coinbase.Wallet.create",
            return_value=mock_wallet,
        ) as mock_create,
    ):
        wallet = WalletCoinbase(config=WalletCoinbaseConfig())

        assert wallet.wallet == mock_wallet
        assert wallet.balance == 0.0
        mock_configure.assert_called_once_with("k", "s")
        mock_create.assert_called_once()


def test_initialization_wallet_fetch_failure():
    """Wallet.fetch failure should be handled gracefully."""
    env = {
        "COINBASE_WALLET_ID": "test_wallet_id",
        "COINBASE_API_KEY": "k",
        "COINBASE_API_SECRET": "s",
    }

    with (
        patch.dict(os.environ, env, clear=True),
        patch("inputs.plugins.wallet_coinbase.Cdp.configure"),
        patch("inputs.plugins.wallet_coinbase.Wallet.fetch") as mock_fetch,
    ):
        mock_fetch.side_effect = Exception("Network error")

        wallet = WalletCoinbase(config=WalletCoinbaseConfig())

        assert wallet.wallet is None
        assert wallet.balance == 0.0
        assert wallet.balance_previous == 0.0


def test_initialization_successful_wallet_fetch():
    """Successful wallet fetch should initialize balances."""
    mock_wallet = MagicMock()
    mock_wallet.balance.return_value = "1.5"

    env = {
        "COINBASE_WALLET_ID": "test_wallet_id",
        "COINBASE_API_KEY": "k",
        "COINBASE_API_SECRET": "s",
    }

    with (
        patch.dict(os.environ, env, clear=True),
        patch("inputs.plugins.wallet_coinbase.Cdp.configure"),
        patch(
            "inputs.plugins.wallet_coinbase.Wallet.fetch",
            return_value=mock_wallet,
        ),
    ):
        wallet = WalletCoinbase(config=WalletCoinbaseConfig())

        assert wallet.wallet == mock_wallet
        assert wallet.balance == 1.5
        assert wallet.balance_previous == 1.5


@pytest.mark.asyncio
async def test_poll_returns_zero_change_when_wallet_missing():
    """Polling without a wallet should return zero change."""
    with patch.dict(os.environ, {}, clear=True):
        wallet = WalletCoinbase(config=WalletCoinbaseConfig())

        result = await wallet._poll()
        assert result == [0.0, 0.0]


@pytest.mark.asyncio
async def test_poll_successful_wallet_refresh():
    """Polling should return correct balance delta."""
    mock_wallet = MagicMock()
    mock_wallet.balance.return_value = "2.0"

    env = {
        "COINBASE_WALLET_ID": "test_wallet_id",
        "COINBASE_API_KEY": "k",
        "COINBASE_API_SECRET": "s",
    }

    with (
        patch.dict(os.environ, env, clear=True),
        patch("inputs.plugins.wallet_coinbase.Cdp.configure"),
        patch(
            "inputs.plugins.wallet_coinbase.Wallet.fetch",
            return_value=mock_wallet,
        ),
    ):
        wallet = WalletCoinbase(config=WalletCoinbaseConfig())
        wallet.balance_previous = 1.5

        result = await wallet._poll()
        assert result == [2.0, 0.5]


def test_raw_to_text_positive_balance_change():
    wallet = WalletCoinbase(config=WalletCoinbaseConfig())

    result = pytest.run(asyncio=True)(
        wallet._raw_to_text([2.0, 0.5])
    )

    assert result is not None
    assert isinstance(result, Message)
    assert result.message == "0.50000"


def test_formatted_latest_buffer_combines_transactions():
    wallet = WalletCoinbase(config=WalletCoinbaseConfig())

    wallet.messages = [
        Message(timestamp=1.0, message="0.5"),
        Message(timestamp=2.0, message="0.3"),
        Message(timestamp=3.0, message="0.2"),
    ]

    result = wallet.formatted_latest_buffer()

    assert result is not None
    assert "You just received 1.00000 ETH." in result
    assert wallet.messages == []
