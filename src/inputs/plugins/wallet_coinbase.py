import asyncio
import logging
import os
import time
from typing import List, Optional

from cdp import Cdp, Wallet
from pydantic import Field

from inputs.base import Message, SensorConfig
from inputs.base.loop import FuserInput
from providers.io_provider import IOProvider


class WalletCoinbaseConfig(SensorConfig):
    """
    Configuration for Wallet Coinbase Sensor.
    """

    asset_id: str = Field(default="eth", description="Asset ID to query")


class WalletCoinbase(FuserInput[WalletCoinbaseConfig, List[float]]):
    """
    Queries current balance of the configured asset and reports a balance increase.
    """

    def __init__(self, config: WalletCoinbaseConfig):
        super().__init__(config)

        self.asset_id = self.config.asset_id
        self.io_provider = IOProvider()
        self.messages: List[Message] = []

        self.POLL_INTERVAL = 0.5
        self.COINBASE_WALLET_ID = os.environ.get("COINBASE_WALLET_ID")

        if self.COINBASE_WALLET_ID:
            logging.info("Coinbase wallet ID configured")
        else:
            logging.warning("COINBASE_WALLET_ID not set")

        API_KEY = os.environ.get("COINBASE_API_KEY")
        API_SECRET = os.environ.get("COINBASE_API_SECRET")

        api_keys_present = False
        if not API_KEY or not API_SECRET:
            logging.error(
                "COINBASE_API_KEY or COINBASE_API_SECRET environment variable is not set"
            )
        else:
            Cdp.configure(API_KEY, API_SECRET)
            api_keys_present = True

        try:
            if self.COINBASE_WALLET_ID:
                self.wallet = Wallet.fetch(self.COINBASE_WALLET_ID)
                logging.info(f"Wallet loaded: {self.wallet}")

            elif api_keys_present:
                logging.info(
                    "COINBASE_WALLET_ID not provided. Creating new Coinbase wallet..."
                )
                self.wallet = Wallet.create()
                logging.warning(
                    f"NEW WALLET CREATED! ID: {self.wallet.id}\n"
                    "Set COINBASE_WALLET_ID to persist this wallet."
                )

            else:
                raise ValueError(
                    "Cannot initialize wallet: missing wallet ID and API keys"
                )

            self.balance = float(self.wallet.balance(self.asset_id))  # type: ignore
            self.balance_previous = self.balance

        except Exception as e:
            logging.error(f"Failed to initialize Coinbase wallet: {e}")
            self.wallet = None
            self.balance = 0.0
            self.balance_previous = 0.0

        logging.info("WalletCoinbase initialized")

    async def _poll(self) -> List[float]:
        await asyncio.sleep(self.POLL_INTERVAL)

        if not self.wallet or not self.COINBASE_WALLET_ID:
            return [self.balance, 0.0]

        try:
            self.wallet = Wallet.fetch(self.COINBASE_WALLET_ID)
            new_balance = float(self.wallet.balance(self.asset_id))
            balance_change = new_balance - self.balance_previous

            self.balance_previous = new_balance
            self.balance = new_balance

        except Exception as e:
            logging.error(f"Error refreshing wallet data: {e}")
            balance_change = 0.0

        return [self.balance, balance_change]

    async def _raw_to_text(self, raw_input: List[float]) -> Optional[Message]:
        balance_change = raw_input[1]

        if balance_change <= 0:
            return None

        return Message(
            timestamp=time.time(),
            message=f"{balance_change:.5f}",
        )

    async def raw_to_text(self, raw_input: List[float]):
        pending_message = await self._raw_to_text(raw_input)
        if pending_message:
            self.messages.append(pending_message)

    def formatted_latest_buffer(self) -> Optional[str]:
        if not self.messages:
            return None

        total_received = sum(float(msg.message) for msg in self.messages)
        last_message = self.messages[-1]

        result_message = Message(
            timestamp=last_message.timestamp,
            message=f"You just received {total_received:.5f} {self.asset_id.upper()}.",
        )

        self.io_provider.add_input(
            self.__class__.__name__,
            result_message.message,
            result_message.timestamp,
        )

        self.messages.clear()

        return f"""
{self.__class__.__name__} INPUT
// START
{result_message.message}
// END
"""
