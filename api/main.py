from fastapi import FastAPI
from api.routes import auth, users, wishlist

app = FastAPI()

app.include_router(router=wishlist.router, prefix='/wishlist',tags=['Wishlist'])
app.include_router(router=users.router, prefix='/users',tags=['Users'])
app.include_router(router=auth.router, prefix='/auth',tags=['Auth'])
