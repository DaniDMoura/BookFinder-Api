from fastapi import APIRouter, Depends
from api.controller import WishlistController, AuthController
from api.models import Users
from api.database import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from http import HTTPStatus
from api.schemas import ListWishlist, AddWishlist

router = APIRouter()

@router.get("/", status_code=HTTPStatus.OK, response_model=ListWishlist)
async def read_books(
    session: AsyncSession = Depends(get_session),
    current_user: Users = Depends(AuthController.get_current_user)
):
    return await WishlistController.show_books(session=session, current_user=current_user)

@router.post("/", status_code=HTTPStatus.CREATED, response_model=AddWishlist)
async def insert_books(
    title: str,
    author: str,
    publisher: str,
    published_date: str,
    description: str,
    page_count: str,
    buylink: str,
    language: str,
    session: AsyncSession = Depends(get_session),
    current_user: Users = Depends(AuthController.get_current_user)
):
    return await WishlistController.add_book(
        title=title,
        author=author,
        publisher=publisher,
        published_date=published_date,
        description=description,
        page_count=page_count,
        buylink=buylink,
        language=language,
        session=session,
        current_user=current_user
    )

@router.delete("/{book_id}", status_code=HTTPStatus.OK)
async def delete_books(
    book_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: Users = Depends(AuthController.get_current_user)
):
    return await WishlistController.delete_book(
        book_id=book_id,
        session=session,
        current_user=current_user
    )
