from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel
app = FastAPI()

class Phone(BaseModel):
    name : str
    price : float
    is_5g : Union[bool, None] = None


@app.get("/")
def home():
    return {"msg":" Welcome to Test FastAPI! "}

@app.get("/items/{item_id}")
def get_item(item_id:int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q }

@app.put("/items/")
def update_phone(phone : Phone):
    return {"msg": phone.name,"price":phone.price}
