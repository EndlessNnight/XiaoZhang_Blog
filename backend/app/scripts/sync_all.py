import subprocess
import sys
import os

def run_sync():
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    
    print("开始同步电影...")
    movie_script = os.path.join(scripts_dir, 'sync_jellyfin.py')
    subprocess.run([sys.executable, movie_script])
    
    print("\n开始同步电视剧...")
    tv_script = os.path.join(scripts_dir, 'sync_jellyfin_tv.py')
    subprocess.run([sys.executable, tv_script])
    
    print("\n开始同步TMDB评分...")
    rating_script = os.path.join(scripts_dir, 'sync_tmdb_ratings.py')
    subprocess.run([sys.executable, rating_script])
    
    print("\n所有同步完成！")

if __name__ == "__main__":
    run_sync() 