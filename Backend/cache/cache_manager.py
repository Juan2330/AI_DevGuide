import os
import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from config import Config

class CacheManager:
    def __init__(self):
        self.cache_dir = Path(Config.CACHE_DIR)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
    def _get_cache_path(self, key):
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.json"
        
    def get(self, key):
        if not Config.CACHE_ENABLED:
            return None
            
        cache_file = self._get_cache_path(key)
        
        if not cache_file.exists():
            return None
            
        file_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
        if file_age > timedelta(days=Config.MAX_CACHE_AGE_DAYS):
            cache_file.unlink()
            return None
            
        with open(cache_file, 'r', encoding='utf-8') as f:
            return json.load(f)
            
    def set(self, key, data):
        if not Config.CACHE_ENABLED:
            return
            
        cache_file = self._get_cache_path(key)
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

cache = CacheManager()