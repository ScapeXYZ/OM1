from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class OrderRequest(BaseModel):
    action: str
    item: str

@app.post("/om1/order")
async def order_item(req: OrderRequest):
    # For now just echo back
    return {"status": "ok", "action": req.action, "item": req.item}
