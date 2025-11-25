from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict

app = FastAPI()

# In-memory store for demo
orders: Dict[str, dict] = {}


class CreateOrderRequest(BaseModel):
    item: str          # e.g. "pizza"
    amount: float      # e.g. 5.0
    wallet: str        # user wallet address


class ConfirmPaymentRequest(BaseModel):
    order_id: str
    tx_hash: str       # transaction hash from wallet


@app.post("/api/create-order")
async def create_order(req: CreateOrderRequest):
    """
    OM1 calls this to create an order and request a payment.
    """
    order_id = f"order_{len(orders) + 1}"

    orders[order_id] = {
        "item": req.item,
        "amount": req.amount,
        "wallet": req.wallet,
        "status": "pending",
        "tx_hash": None,
    }

    # This JSON MUST be valid – OM1 will parse it.
    return {
        "order_id": order_id,
        "status": "pending",
        "message": f"Created order for {req.item} costing {req.amount} to be paid from wallet {req.wallet}",
    }


@app.post("/api/confirm-payment")
async def confirm_payment(req: ConfirmPaymentRequest):
    """
    OM1 calls this after the user signs the transaction in the wallet.
    """
    if req.order_id not in orders:
        return {"error": "order_not_found"}

    orders[req.order_id]["status"] = "paid"
    orders[req.order_id]["tx_hash"] = req.tx_hash

    return {
        "order_id": req.order_id,
        "status": "paid",
        "tx_hash": req.tx_hash,
        "message": "Payment confirmed",
    }


@app.get("/")
async def home():
    return {"status": "wallet-backend-running"}
