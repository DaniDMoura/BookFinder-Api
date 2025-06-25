from __future__ import annotations

from pydantic import BaseModel
from typing import List
from datetime import date


class User(BaseModel):
    id: int
    username: str
    password: str


class Users(BaseModel):
    Users: List[User]


class UserCreate(BaseModel):
    username: str
    password: str


class Wishlist(BaseModel):
    id: int
    title: str
    author: str
    publisher: str
    published_date: date
    description: str
    page_count: int
    buy_link: str
    language: str
    user_id: int


class ListWishlist(BaseModel):
    books: List[Wishlist]


class AddWishlist(BaseModel):
    message: str
    book_id: int
