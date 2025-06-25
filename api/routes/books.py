from fastapi import APIRouter

router = APIRouter()



@router.get("/")
async def get_books(name: str):
  return await ...