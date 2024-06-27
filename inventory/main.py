import os

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from redis_om import HashModel, get_redis_connection

load_dotenv()

REDIS_HOST_NAME = os.getenv("REDIS_HOST_NAME")
REDIS_PORT_NO = os.getenv("REDIS_PORT_NO")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

app = FastAPI()

origins = ['http://localhost:3000', 'http://localhost:8501']
app.add_middleware(CORSMiddleware, allow_origins = origins, allow_methods=["*"], allow_headers=["*"])

redis = get_redis_connection(
    host=REDIS_HOST_NAME,
    port=REDIS_PORT_NO,
    password=REDIS_PASSWORD,
    decode_responses = True
)

class Product(HashModel):
    name: str
    quantity: int
    price: float

    class Meta:
        database = redis

@app.get("/products")
async def getall():
    return [format(pk) for pk in Product.all_pks()] #Returns all primary keys

def format(pk : str):
    product = Product.get(pk=pk)
    return {
        'id' : product.pk,
        'name' : product.name,
        'quantity' : product.quantity,
        'price' : product.price
    }

@app.post("/products")
async def createproducts(product : Product):
    return product.save()

@app.get("/products/{pk}")
async def getsingleproduct(pk : str):
    return Product.get(pk=pk)

@app.delete("/products/{pk}")
async def deleteproduct(pk : str):
    return Product.delete(pk=pk) #Returns 1 when successfully deleted

if __name__=="__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=5000, reload=True)