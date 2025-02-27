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
from models import Movie
from database import SessionLocal

load_dotenv()

class JellyfinClient:
    def __init__(self):
        self.base_url = os.getenv("JELLYFIN_URL")
        self.api_key = os.getenv("JELLYFIN_API_KEY")
        self.user_id = os.getenv("JELLYFIN_USER_ID")
        self.headers = {
            'X-MediaBrowser-Token': self.api_key,
            'Content-Type': 'application/json'
        }

    def get_library_items(self, library_type="Series"):
        """获取指定类型的媒体库内容"""
        url = f"{self.base_url}/Users/{self.user_id}/Items"
        params = {
            'IncludeItemTypes': library_type,
            'Recursive': 'true',
            'Fields': 'ProviderIds,DateCreated,PlaybackInfo,UserData,Path,PremiereDate,Studios,Genres,SeasonCount,EpisodeCount',
            'SortBy': 'DateCreated,SortName',
            'SortOrder': 'Descending',
            'EnableImageTypes': 'Primary,Backdrop',
            'ImageTypeLimit': 1,
            'EnableImages': True,
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params, verify=False)
            response.raise_for_status()
            return response.json().get('Items', [])
        except Exception as e:
            print(f"从Jellyfin获取媒体库失败: {str(e)}")
            return []

    def get_item_details(self, item_id):
        """获取单个项目的详细信息"""
        url = f"{self.base_url}/Users/{self.user_id}/Items/{item_id}"
        try:
            response = requests.get(url, headers=self.headers, verify=False)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"获取项目详情失败 (ID: {item_id}): {str(e)}")
            return None

@sleep_and_retry
@limits(calls=1, period=1)
def get_tmdb_info(tmdb_id):
    """从TMDB获取电视剧详细信息（带速率限制）"""
    tmdb_api_key = "459906f3a00258e919f2f6792482ae1b"
    url = f"https://api.themoviedb.org/3/tv/{tmdb_id}"
    params = {
        'api_key': tmdb_api_key,
        'language': 'zh-CN',
        'append_to_response': 'credits,keywords'
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"从TMDB获取电视剧信息失败 (ID: {tmdb_id}): {str(e)}")
        return None

def process_tv_data(jellyfin_tv, tmdb_info):
    """处理电视剧数据"""
    # 获取观看状态
    user_data = jellyfin_tv.get('UserData', {})
    played = user_data.get('Played', False)
    played_percentage = user_data.get('PlayedPercentage', 0)
    unplayed_items = user_data.get('UnplayedItemCount', 0)
    total_episodes = jellyfin_tv.get('EpisodeCount', 0)
    
    # 根据播放进度确定观看状态
    if played or (total_episodes > 0 and unplayed_items == 0):
        watch_status = 'watched'
    elif played_percentage > 0 or (total_episodes > 0 and unplayed_items < total_episodes):
        watch_status = 'watching'
    else:
        watch_status = 'want_to_watch'

    # 处理类型和子类型
    studios = jellyfin_tv.get('Studios', [])
    studio_names = [s.get('Name', '') for s in studios]
    sub_type = 'other'
    
    if any(s for s in studio_names if '中国' in s or '香港' in s or '台湾' in s):
        sub_type = 'chinese'
    elif any(s for s in studio_names if '日本' in s or '韩国' in s):
        sub_type = 'asian'
    elif any(s for s in studio_names if '美国' in s or '英国' in s or '法国' in s):
        sub_type = 'western'

    # 处理观看日期
    watch_date = user_data.get('LastPlayedDate')
    if watch_date:
        try:
            watch_date = datetime.strptime(watch_date.split('.')[0], '%Y-%m-%dT%H:%M:%S')
        except Exception as e:
            print(f"处理观看日期出错: {str(e)}")
            watch_date = None

    # 处理发布日期
    release_date = tmdb_info.get('first_air_date')
    if release_date:
        try:
            release_date = datetime.strptime(release_date, '%Y-%m-%d').strftime('%Y-%m-%d')
        except Exception as e:
            print(f"处理发布日期出错: {str(e)}")
            release_date = None

    return {
        'tmdb_id': int(jellyfin_tv['ProviderIds']['Tmdb']),
        'title': tmdb_info.get('name', ''),
        'original_title': tmdb_info.get('original_name', ''),
        'poster_path': f"https://image.tmdb.org/t/p/w500{tmdb_info.get('poster_path')}" if tmdb_info.get('poster_path') else None,
        'backdrop_path': f"https://image.tmdb.org/t/p/w500{tmdb_info.get('backdrop_path')}" if tmdb_info.get('backdrop_path') else None,
        'overview': tmdb_info.get('overview', ''),
        'release_date': release_date,
        'type': 'tv',
        'sub_type': sub_type,
        'genres': ','.join([g['name'] for g in tmdb_info.get('genres', [])]),
        'watch_status': watch_status,
        'rating': user_data.get('UserRating', 0),
        'comment': None,
        'watch_date': watch_date,
        'updated_at': datetime.now(),
        'is_deleted': False,
        'deleted_at': None
    }

def sync_tv_shows():
    """同步电视剧信息到数据库"""
    client = JellyfinClient()
    db = SessionLocal()
    
    try:
        # 获取Jellyfin中的电视剧
        jellyfin_tvs = client.get_library_items()
        total_tvs = len(jellyfin_tvs)
        print(f"开始同步 {total_tvs} 部电视剧 - {datetime.now()}")
        
        for index, jf_tv in enumerate(jellyfin_tvs, 1):
            try:
                # 检查是否有TMDB ID
                provider_ids = jf_tv.get('ProviderIds', {})
                if 'Tmdb' not in provider_ids:
                    print(f"跳过没有TMDB ID的电视剧: {jf_tv.get('Name', 'Unknown')}")
                    continue

                tmdb_id = int(provider_ids['Tmdb'])
                print(f"处理第 {index}/{total_tvs} 部电视剧: {jf_tv.get('Name')} (TMDB ID: {tmdb_id})")

                # 获取详细信息
                item_details = client.get_item_details(jf_tv['Id'])
                if not item_details:
                    continue

                # 获取TMDB信息
                tmdb_info = get_tmdb_info(tmdb_id)
                if not tmdb_info:
                    continue

                # 处理电视剧数据
                tv_data = process_tv_data(item_details, tmdb_info)

                # 更新或创建记录
                existing_tv = db.query(Movie).filter(
                    Movie.tmdb_id == tmdb_id,
                    Movie.is_deleted == False
                ).first()

                if existing_tv:
                    print(f"更新现有电视剧: {tv_data['title']}")
                    for key, value in tv_data.items():
                        setattr(existing_tv, key, value)
                else:
                    print(f"添加新电视剧: {tv_data['title']}")
                    new_tv = Movie(**tv_data)
                    db.add(new_tv)

                # 每10部电视剧提交一次
                if index % 10 == 0:
                    db.commit()
                    print(f"已处理 {index}/{total_tvs} 部电视剧")

            except Exception as e:
                print(f"处理电视剧时出错: {str(e)}")
                continue

        # 提交剩余更改
        db.commit()
        print(f"同步完成，共处理 {total_tvs} 部电视剧")

    except Exception as e:
        print(f"同步过程中出错: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    start_time = time.time()
    print(f"开始同步 - {datetime.now()}")
    sync_tv_shows()
    end_time = time.time()
    duration = end_time - start_time
    print(f"同步结束 - {datetime.now()}")
    print(f"总耗时: {duration:.2f} 秒") 