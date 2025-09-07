from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, status, Response
from pydantic import BaseModel, Field
from threading import Lock

app = FastAPI(title="Items API", version="1.0")

class ItemCreate(BaseModel):
    name : str = Field(...,min_length=2)
    price : float = Field(...,ge=0)
    is_5g : Optional[bool] = None

class Item(ItemCreate):
    item_id : int

    
items :Dict[int,Item] = {}
_next_id = 1
_store_lock = Lock()

@app.get("/api/v1/", tags=['health'])
def home():
    return {"message":" Welcome to Test FastAPI! "}

@app.get("/api/v1/items", response_model=List[Item])
def list_items():
    # Return a list rather than a raw dict for easier client consumption
    return list(items.values())

@app.get("/api/v1/items/{item_id}",response_model=Item)
def get_item(item_id:int):
    if item_id in items:
        return items[item_id]
    else:
        raise HTTPException(status_code=404, detail="Item not found")
    
@app.post("/api/v1/items", response_model= Item, status_code=201)
def create_item(payload :ItemCreate):
    global _next_id
    with _store_lock:
        item_id = _next_id
        _next_id += 1
        # The payload is coming in ItemCreate form, convert
        # it into dict with model_dump (dict() is deprecated)
        # This dict can be unpacked into kwargs like
        # name='phone',price=20 with **
        item = Item(item_id = item_id, **payload.model_dump())
        items[item_id] = item
    print(items)
    return item

@app.put("/api/v1/items/{item_id}", response_model= Item)
def update_item(item_id : int, payload : ItemCreate):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    else:
        with _store_lock:
            # payload is of ItemCreate type it has no item_id
            # So we cant just do items[item_id] = payload
            # So 1st extract the payload with model_dump
            # then update the item at its position with dumped data
            existing = items[item_id]
            updated = existing.model_copy(update= payload.model_dump())
            items[item_id] = updated
        return updated
    # We can also pass exclude_unset to model_dump()
    # so only fields set by client are used for updation
    # rest are ignored

    # There are two ways of achieving the above : 
    # 1. PUT (replace all fields):

    # updated = Item(item_id=item_id, **payload.model_dump())
    # items[item_id] = updated

    # → simple and clear, assumes client sends all required fields.

    # 2. PATCH (partial update):

    # existing = items[item_id]
    # updated = existing.model_copy(update=payload.model_dump(exclude_unset=True))
    # items[item_id] = updated

    # → keeps old fields when client only sends a subset.

@app.delete("/api/v1/items/{item_id}", status_code=204)
def delete_item(item_id :int ):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    with _store_lock:
        del items[item_id]
    return Response(status_code=status.HTTP_204_NO_CONTENT)