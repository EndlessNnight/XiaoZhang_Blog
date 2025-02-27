import httpx
from typing import Optional, Dict, Any, List
from ..core.config import settings

TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"

class TMDBClient:
    def __init__(self):
        self.api_key = settings.TMDB_API_KEY
        self.base_url = "https://api.themoviedb.org/3"
        self.language = "zh-CN"
    
    async def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict:
        """发送请求到TMDB API"""
        if params is None:
            params = {}
        
        params.update({
            "api_key": self.api_key,
            "language": self.language
        })
        
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}{endpoint}", params=params)
            response.raise_for_status()
            return response.json()
    
    async def search_movies(self, query: str, page: int = 1) -> Dict:
        """搜索电影"""
        try:
            data = await self._make_request("/search/movie", {"query": query, "page": page})
            results = data.get("results", [])
            
            formatted_results = [
                {
                    "tmdb_id": item["id"],
                    "title": item.get("title", ""),
                    "original_title": item.get("original_title", ""),
                    "poster_path": f"{TMDB_IMAGE_BASE_URL}{item['poster_path']}" if item.get("poster_path") else None,
                    "backdrop_path": f"{TMDB_IMAGE_BASE_URL}{item['backdrop_path']}" if item.get("backdrop_path") else None,
                    "overview": item.get("overview", ""),
                    "release_date": item.get("release_date"),
                    "vote_average": item.get("vote_average"),
                    "popularity": item.get("popularity"),
                    "media_type": "movie",
                    "genre_ids": item.get("genre_ids", [])
                }
                for item in results
            ]
            
            return {
                "results": formatted_results,
                "total_results": data.get("total_results", 0),
                "page": data.get("page", 1),
                "total_pages": data.get("total_pages", 1)
            }
            
        except Exception as e:
            print(f"搜索电影出错: {str(e)}")
            return {"results": [], "total_results": 0, "page": 1, "total_pages": 1}
    
    async def search_tv(self, query: str, page: int = 1) -> Dict:
        """搜索电视剧"""
        try:
            data = await self._make_request("/search/tv", {"query": query, "page": page})
            results = data.get("results", [])
            
            formatted_results = [
                {
                    "tmdb_id": item["id"],
                    "title": item.get("name", ""),
                    "original_title": item.get("original_name", ""),
                    "poster_path": f"{TMDB_IMAGE_BASE_URL}{item['poster_path']}" if item.get("poster_path") else None,
                    "backdrop_path": f"{TMDB_IMAGE_BASE_URL}{item['backdrop_path']}" if item.get("backdrop_path") else None,
                    "overview": item.get("overview", ""),
                    "release_date": item.get("first_air_date"),
                    "vote_average": item.get("vote_average"),
                    "popularity": item.get("popularity"),
                    "media_type": "tv",
                    "genre_ids": item.get("genre_ids", [])
                }
                for item in results
            ]
            
            return {
                "results": formatted_results,
                "total_results": data.get("total_results", 0),
                "page": data.get("page", 1),
                "total_pages": data.get("total_pages", 1)
            }
            
        except Exception as e:
            print(f"搜索电视剧出错: {str(e)}")
            return {"results": [], "total_results": 0, "page": 1, "total_pages": 1}

tmdb_client = TMDBClient()

async def get_movie_info(query: str) -> Dict[str, Any]:
    """搜索电影信息"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{settings.TMDB_BASE_URL}/search/movie",
                params={
                    "api_key": settings.TMDB_API_KEY,
                    "query": query,
                    "language": "zh-CN"
                }
            )
            response.raise_for_status()
            data = response.json()
            results = data.get("results", [])
            
            # 处理结果，添加完整的图片路径
            formatted_results = [
                {
                    "tmdb_id": item["id"],
                    "title": item.get("title", ""),
                    "original_title": item.get("original_title", ""),
                    "poster_path": f"{TMDB_IMAGE_BASE_URL}{item['poster_path']}" if item.get("poster_path") else None,
                    "backdrop_path": f"{TMDB_IMAGE_BASE_URL}{item['backdrop_path']}" if item.get("backdrop_path") else None,
                    "overview": item.get("overview", ""),
                    "release_date": item.get("release_date"),
                    "type": "movie"
                }
                for item in results
            ]
            return formatted_results
        except Exception as e:
            print(f"TMDB API Error: {str(e)}")
            return []

async def get_tv_info(query: str) -> Dict[str, Any]:
    """搜索电视剧信息"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{settings.TMDB_BASE_URL}/search/tv",
                params={
                    "api_key": settings.TMDB_API_KEY,
                    "query": query,
                    "language": "zh-CN"
                }
            )
            response.raise_for_status()
            data = response.json()
            results = data.get("results", [])
            
            # 处理结果，添加完整的图片路径
            formatted_results = [
                {
                    "tmdb_id": item["id"],
                    "title": item.get("name", ""),
                    "original_title": item.get("original_name", ""),
                    "poster_path": f"{TMDB_IMAGE_BASE_URL}{item['poster_path']}" if item.get("poster_path") else None,
                    "backdrop_path": f"{TMDB_IMAGE_BASE_URL}{item['backdrop_path']}" if item.get("backdrop_path") else None,
                    "overview": item.get("overview", ""),
                    "release_date": item.get("first_air_date"),
                    "type": "tv"
                }
                for item in results
            ]
            return formatted_results
        except Exception as e:
            print(f"TMDB API Error: {str(e)}")
            return []

async def get_movie_details(movie_id: int) -> Dict[str, Any]:
    """获取电影详细信息"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.TMDB_BASE_URL}/movie/{movie_id}",
            params={
                "api_key": settings.TMDB_API_KEY,
                "language": "zh-CN",
                "append_to_response": "credits,images"
            }
        )
        response.raise_for_status()
        return response.json()

async def get_tv_details(tv_id: int) -> Dict[str, Any]:
    """获取电视剧详细信息"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.TMDB_BASE_URL}/tv/{tv_id}",
            params={
                "api_key": settings.TMDB_API_KEY,
                "language": "zh-CN",
                "append_to_response": "credits,images"
            }
        )
        response.raise_for_status()
        return response.json() 