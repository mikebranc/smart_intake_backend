from fastapi import APIRouter, HTTPException

router = APIRouter(
    prefix="/items",
    tags=["items"]
)

@router.get("/")
async def read_items():
    return [{"name": "Item 1"}, {"name": "Item 2"}]

@router.get("/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id, "name": f"Item {item_id}"}