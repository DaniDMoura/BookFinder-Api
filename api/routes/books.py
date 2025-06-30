from __future__ import annotations

from fastapi import APIRouter, Depends
from api.controller import BookController, AuthController
from http import HTTPStatus
from api.models import Users
from api.schemas import RequestBooks

router = APIRouter()


@router.get("/", status_code=HTTPStatus.OK, response_model=RequestBooks)
async def get_books(
    query: str, current_user: Users = Depends(AuthController.get_current_user)
):
    return await BookController.request_book_data(
        query=query, current_user=current_user
    )
