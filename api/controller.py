from datetime import datetime, timedelta
from http import HTTPStatus
from zoneinfo import ZoneInfo
from pwdlib import PasswordHash
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import DecodeError, ExpiredSignatureError, decode, encode
from api.settings import Settings
from api.database import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from api.models import Users, Wishlist
from sqlalchemy import select
from httpx import AsyncClient

settings = Settings()
pwd_context = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth')

class AuthController():
  @staticmethod
  async def verify_login(username: str, password: str, session: AsyncSession = Depends(get_session)):
    login_exception = HTTPException(
      status_code=HTTPStatus.UNAUTHORIZED,
      detail='Incorrect username or password'
    )

    user = await session.scalar(
      select(Users).where(Users.username == username)
    )

    if not user:
      raise login_exception

    if not AuthController.verify_password(password, user.password):
      raise login_exception

    access_token = AuthController.create_access_token(data={'sub': user.username})

    return {'access_token': access_token, 'token_type': 'bearer'}

  @staticmethod
  def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

  @staticmethod
  async def get_current_user(
    session: AsyncSession = Depends(get_session),
    token: str = Depends(oauth2_scheme)
  ):
    credentials_exception = HTTPException(
      status_code=HTTPStatus.UNAUTHORIZED,
      detail='Could not validate credentials',
      headers={'WWW-Authenticate': 'Bearer'}
    )

    try:
      payload = decode(
        token, settings.SECRET_KEY, algorithms=settings.ALGORITHM
      )
      subject_username = payload.get('sub')

      if not subject_username:
        raise credentials_exception

    except DecodeError:
      raise credentials_exception

    except ExpiredSignatureError:
      raise credentials_exception

    user = await session.scalar(
      select(Users).where(Users.username == subject_username)
    )

    if not user:
      raise credentials_exception

    return user


  @staticmethod
  def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(tz=ZoneInfo("UTC")) + timedelta(minutes=30)
    to_encode.update({"exp": int(expire.timestamp())})
    encoded_jwt = encode(
      to_encode, settings.SECRET_KEY, algorithm = settings.ALGORITHM
    )
    return encoded_jwt

class UserController():
  @staticmethod
  def get_password_hash(password: str):
    return pwd_context.hash(password)

  @staticmethod
  async def create_user(username: str, password: str, session: AsyncSession = Depends(get_session)):
    db_user = await session.scalar(
      select(Users).where(Users.username == username)
    )

    if db_user:
      if db_user.username == username:
        raise HTTPException(
          status_code=HTTPStatus.CONFLICT,
          detail='Username already exists'
        )

    hashed_password = UserController.get_password_hash(password)

    db_user = Users(
      username = username,
      password = hashed_password
    )

    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)

    return db_user


  @staticmethod
  async def delete_user(user_id: int, session: AsyncSession = Depends(get_session), current_user: Users = Depends(AuthController.get_current_user)):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Not enough permissions'
        )

    user = await session.scalar(select(Users).where(Users.id == current_user.id))

    await session.delete(user)
    await session.commit()

    return {'message': 'User deleted'}

class WishlistController():
  @staticmethod
  async def add_book(
    title: str,
    author: str,
    publisher: str,
    published_date: str,
    description: str,
    page_count: str,
    buylink: str,
    language: str,
    current_user: Users = Depends(AuthController.get_current_user),
    session: AsyncSession = Depends(get_session)
  ):
    new_book = Wishlist(
      title= title,
      author = author,
      publisher= publisher,
      published_date= published_date,
      description= description,
      page_count= page_count,
      buylink= buylink,
      language= language,
      user_id= current_user.id,
    )
    session.add(new_book)
    await session.commit()
    await session.refresh(new_book)

    return {"message": "Book added", "book_id": new_book.id}


  @staticmethod
  async def delete_book(book_id, session: AsyncSession = Depends(get_session), current_user: Users = Depends(AuthController.get_current_user)):
    book = await session.scalar(select(Wishlist).where(
      Wishlist.user_id == current_user.id, Wishlist.id == book_id
    ))

    if not book:
      raise HTTPException(
        detail="No books found",
        status_code=HTTPStatus.NOT_FOUND
      )

    await session.delete(book)
    await session.commit()

    return {"detail": "Book deleted"}

  @staticmethod
  async def show_books(
    session: AsyncSession = Depends(get_session),
    current_user: Users = Depends(AuthController.get_current_user)
  ):
    books = (await session.scalars(select(Wishlist).where(Wishlist.user_id == current_user.id))).all()

    if not books:
      raise HTTPException(
        detail="No books found",
        status_code=HTTPStatus.NOT_FOUND
      )

    return {'books': books }

class BookController(WishlistController):
    @staticmethod
    async def request_book_data(
        name: str,
        current_user: Users = Depends(AuthController.get_current_user)
    ) -> list[dict]:
        url = "https://www.googleapis.com/books/v1/volumes"
        params = {
            "q": name,
            "key": settings.GOOGLE_BOOKS_API_KEY,
            "maxResults": 40,
        }

        async with AsyncClient(timeout=10) as client:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = await response.json()
            except Exception as e:
                raise HTTPException(
                    status_code=HTTPStatus.BAD_REQUEST,
                    detail=f"Error requesting data: {e}",
                )

        books = data.get("items", [])
        book_details = []

        for book in books:
            info = book.get("volumeInfo", {})
            sale_info = book.get("saleInfo", {})

            title = info.get("title", "Unknown")
            authors = ", ".join(info.get("authors", ["Unknown"]))
            publisher = info.get("publisher", "Unknown")
            published_date = info.get("publishedDate", "Unknown")
            image = info.get("imageLinks", {}).get("thumbnail")
            description = info.get("description", "No description available")
            buy_link = sale_info.get("buyLink", None)
            language = info.get("language", "Unknown")
            page_count = info.get("pageCount", 0)

            book_details.append({
                "title": title,
                "authors": authors,
                "publisher": publisher,
                "published_date": published_date,
                "image": image,
                "description": description,
                "buy_link": buy_link,
                "language": language,
                "page_count": page_count,
            })

        return book_details

