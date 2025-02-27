import requests
import os
from datetime import datetime
import sys
import time
from ratelimit import limits, sleep_and_retry
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker

# 添加父目录到系统路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from app.core.database import SessionLocal
from app.models import Movie

load_dotenv()

@sleep_and_retry
@limits(calls=1, period=1)  # 限制为每秒1次请求
def get_tmdb_rating(tmdb_id, media_type="movie"):
    """从TMDB获取评分信息"""
    tmdb_api_key = "459906f3a00258e919f2f6792482ae1b"
    url = f"https://api.themoviedb.org/3/{media_type}/{tmdb_id}"
    params = {
        'api_key': tmdb_api_key,
        'language': 'zh-CN'
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        # TMDB的评分是10分制，转换为5星制
        vote_average = data.get('vote_average', 0)
        vote_count = data.get('vote_count', 0)
        
        # 只有当有足够多的评分时才考虑
        if vote_count >= 100:
            rating = (vote_average / 2)  # 转换为5星制
            return round(rating, 1)  # 保留一位小数
        return None
    except Exception as e:
        print(f"获取TMDB评分失败 (ID: {tmdb_id}): {str(e)}")
        return None

def sync_ratings():
    """同步所有影视的TMDB评分"""
    db = SessionLocal()
    try:
        # 获取所有未删除的影视
        movies = db.query(Movie).filter(Movie.is_deleted == False).all()
        total = len(movies)
        print(f"开始同步 {total} 个影视评分 - {datetime.now()}")
        
        updated_count = 0
        skipped_count = 0
        error_count = 0
        
        for index, movie in enumerate(movies, 1):
            try:
                print(f"处理 {index}/{total}: {movie.title} (TMDB ID: {movie.tmdb_id})")
                
                # 如果已经有用户评分，跳过
                if movie.rating > 0:
                    print(f"已有用户评分 ({movie.rating}星)，跳过")
                    skipped_count += 1
                    continue
                
                # 获取TMDB评分
                tmdb_rating = get_tmdb_rating(movie.tmdb_id, movie.type)
                if tmdb_rating is None:
                    print("无有效TMDB评分，跳过")
                    skipped_count += 1
                    continue
                
                # 更新评分
                movie.rating = tmdb_rating
                movie.updated_at = datetime.now()
                updated_count += 1
                print(f"更新评分为: {tmdb_rating}星")
                
                # 每10个提交一次
                if index % 10 == 0:
                    db.commit()
                    print(f"已处理: {index}/{total}")
                
            except Exception as e:
                print(f"处理出错: {str(e)}")
                error_count += 1
                continue
        
        # 提交剩余更改
        db.commit()
        
        # 打印统计信息
        print("\n同步完成!")
        print(f"总数: {total}")
        print(f"更新: {updated_count}")
        print(f"跳过: {skipped_count}")
        print(f"错误: {error_count}")
        
    except Exception as e:
        print(f"同步过程中出错: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    start_time = time.time()
    print(f"开始同步TMDB评分 - {datetime.now()}")
    sync_ratings()
    end_time = time.time()
    duration = end_time - start_time
    print(f"同步结束 - {datetime.now()}")
    print(f"总耗时: {duration:.2f} 秒") 