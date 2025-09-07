from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from threading import Lock

app = FastAPI(title="Items API", version="1.0")

class ItemCreate(BaseModel):
    name : str = Field(...,min_length=2)
    price : float = Field(...,ge=0)
    is_5g : Optional[bool] = None

class Item(BaseModel):
    item_id : int
    
items :Dict[int,Item] = dict()
_next_id = 1
_store_lock = Lock()

@app.get("/api/v1/", tags=['health'])
def home():
    return {"message":" Welcome to Test FastAPI! "}

@app.get("/api/v1/items", response_model=Item)
def get_all_items():
    # Return a list rather than a raw dict for easier client consumption
    return list(items.values())


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
