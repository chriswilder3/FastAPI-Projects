# app/main.py
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, status, Response
from pydantic import BaseModel, Field, model_validator
from threading import Lock


app = FastAPI(title="Items API", version="1.0")

# =====================
# Schemas
# =====================

class ItemBase(BaseModel):
    name: str = Field(..., min_length=2)
    price: float = Field(..., ge=0)
    is_5g: Optional[bool] = None


class ItemCreate(ItemBase):
    """Used for creating a new item (client sends)."""
    pass


class ItemUpdate(BaseModel):
    """Used for updating an item (client sends, all fields optional)."""
    name: Optional[str] = Field(None, min_length=2)
    price: Optional[float] = Field(None, ge=0)
    is_5g: Optional[bool] = None

    @model_validator(mode="before")
    def at_least_one_field(cls, values: dict):
        if not any(values.values()):
            raise ValueError("At least one field must be provided")
        return values

class Item(ItemBase):
    """Used for returning an item (server response)."""
    item_id: int

    class Config:
        orm_mode = True  # Helps when integrating with DB models later

# =====================
# In-memory store
# =====================

items: Dict[int, Item] = {}
_next_id = 1
_store_lock = Lock()


# =====================
# Routes
# =====================

@app.get("/api/v1/", tags=["health"])
def home():
    return {"message": "Welcome to Test FastAPI!"}


@app.get("/api/v1/items", response_model=List[Item])
def list_items():
    return list(items.values())


@app.get("/api/v1/items/{item_id}", response_model=Item)
def get_item(item_id: int):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    return items[item_id]


@app.post("/api/v1/items", response_model=Item, status_code=201)
def create_item(payload: ItemCreate):
    global _next_id
    with _store_lock:
        item_id = _next_id
        _next_id += 1
        item = Item(item_id=item_id, **payload.model_dump())
        items[item_id] = item
    return item


@app.put("/api/v1/items/{item_id}", response_model=Item)
def update_item(item_id: int, payload: ItemUpdate):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")

    with _store_lock:
        existing = items[item_id]
        updated = existing.model_copy(update=payload.model_dump(exclude_unset=True))
        items[item_id] = updated
    return updated


@app.delete("/api/v1/items/{item_id}", status_code=204)
def delete_item(item_id: int):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    with _store_lock:
        del items[item_id]
    return Response(status_code=status.HTTP_204_NO_CONTENT)
