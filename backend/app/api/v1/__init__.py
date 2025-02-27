from fastapi import APIRouter
from . import users, articles, categories, comments, movies
from .users import router as users_router
from .articles import router as articles_router
from .categories import router as categories_router
from .movies import router as movies_router
from .upload import router as upload_router

api_router = APIRouter()

api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(articles_router, prefix="/articles", tags=["articles"])
api_router.include_router(categories_router, prefix="/categories", tags=["categories"])
api_router.include_router(comments.router, prefix="/comments", tags=["comments"])
api_router.include_router(movies_router, prefix="/movies", tags=["movies"])
api_router.include_router(upload_router, prefix="/upload", tags=["upload"]) 