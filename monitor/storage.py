import json
import os
import hashlib
from typing import Dict, Any

class Storage:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self._ensure_dir()
        self.data = self._load()

    def _ensure_dir(self):
        dirname = os.path.dirname(self.file_path)
        if dirname and not os.path.exists(dirname):
            os.makedirs(dirname)

    def _load(self) -> Dict[str, Any]:
        if not os.path.exists(self.file_path):
            return {}
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}

    def save(self):
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def get_site_data(self, url: str) -> Dict[str, Any]:
        return self.data.get(url, {})

    def update_site_data(self, url: str, content: str):
        content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
        self.data[url] = {
            "last_hash": content_hash,
            "last_content": content,
            "last_check": 0 # Timestamp handled by caller if needed
        }
        self.save()
