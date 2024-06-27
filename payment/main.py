import os
import time

import requests
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.background import BackgroundTasks
from fastapi.responses import JSONResponse
from redis_om import HashModel, get_redis_connection
from starlette.requests import Request

load_dotenv()

REDIS_HOST_NAME = os.getenv("REDIS_HOST_NAME")
REDIS_PORT_NO = os.getenv("REDIS_PORT_NO")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

app = FastAPI()

origins = ['http://localhost:3000', 'http://localhost:8501']
app.add_middleware(CORSMiddleware, allow_origins = origins, allow_methods=["*"], allow_headers=["*"])

#Different database from Inventory
redis = get_redis_connection(
    host=REDIS_HOST_NAME,
    port=REDIS_PORT_NO,
    password=REDIS_PASSWORD,
    decode_responses = True
)

class Order(HashModel):
    product_id : str
    price: float
    fee : float
    total: float
    quantity: int
    status: str

    class Meta:
        database = redis

@app.get("/orders/{pk}")
def get(pk :str):
    order = Order.get(pk=pk)
    redis.xadd('refund_completed', order.dict(), "*")
    return order

@app.post("/orders")
async def create(req : Request, background_tasks : BackgroundTasks):
    body = await req.json()
    res = requests.get("http://localhost:5000/products/%s" %body['id'])
    product = res.json()
    order = Order(
        product_id = body['id'],
        price = product['price'],
        fee = 0.2*product['price'],
        total = 1.2*product['price'],
        quantity = body['quantity'],
        status = 'pending'
    )
    order.save()
    background_tasks.add_task(order_completed, order)
    return order

def order_completed(order : Order):
    time.sleep(5)
    order.status = "Completed"
    order.save()
    redis.xadd("order_completed", order.dict(), "*")


if __name__=="__main__":
    uvicorn.run("main:app", host="localhost", port=5001, reload=True)