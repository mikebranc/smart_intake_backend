from fastapi import APIRouter, HTTPException

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.get("/")
async def read_users():
    return [{"username": "user1"}, {"username": "user2"}]

@router.get("/{username}")
async def read_user(username: str):
    return {"username": username}