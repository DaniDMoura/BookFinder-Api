from __future__ import annotations

from fastapi import APIRouter, Depends
from api.controller import AuthController
from api.database import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()


@router.post("/")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session),
):
    return await AuthController.verify_login(
        username=form_data.username, password=form_data.password, session=session
    )
