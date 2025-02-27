from .user import User
from .article import Article
from .category import Category
from .comment import Comment
from .movie import Movie
from .mixins import SoftDeleteMixin

# 为了向后兼容，可以在这里导出所有模型
__all__ = ['User', 'Article', 'Category', 'Comment', 'Movie', 'SoftDeleteMixin'] 