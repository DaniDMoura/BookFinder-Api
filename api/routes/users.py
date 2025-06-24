from fastapi import APIRouter, Depends
from api.controller import UserController, AuthController
from api.schemas import UserCreate
from api.database import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from api.models import Users
from http import HTTPStatus


router = APIRouter()

@router.post('/', status_code=HTTPStatus.CREATED)
async def create_user(
  user: UserCreate,
  session: AsyncSession = Depends(get_session),
  ):
  return await UserController.create_user(
    password=user.password,
    username=user.username,
    session=session
  )

@router.delete('/{user_id}', status_code=HTTPStatus.OK)
async def delete_user(
  user_id: int,
  current_user: Users = Depends(AuthController.get_current_user),
  session: AsyncSession = Depends(get_session),
  ):
  return await UserController.delete_user(
    user_id=user_id,
    current_user=current_user,
    session=session)