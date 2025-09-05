from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    item_id : int
    name : str
    price : float
    is_5g : Union[bool, None] = None

items :dict[int:Item] = dict()

@app.get("/")
def home():
    return {"msg":" Welcome to Test FastAPI! "}

@app.get("/items/{item_id}")
def get_item(item_id:int):
    if item_id in items:
        return {"item":items[item_id]}
    else:
        return {"error":"No such item found"}
@app.post("/items/create")
def create_item(itemReceived :Item):
    items[itemReceived.item_id] = itemReceived
    return {"msg":"creation successful","item_id":itemReceived.item_id}

@app.put("/items/")
def update_phone(itemReceived : Item):
    if "item_id" not in itemReceived:
        return {"error":"Invalid item"}
    if itemReceived.item_id in items:
        items[itemReceived.item_id] = itemReceived
        return {"msg": "update successful","name": itemReceived.name}
    return {"msg":"Something went wrong"}
