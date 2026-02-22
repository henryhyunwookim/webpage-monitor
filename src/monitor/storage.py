import json
import os
import hashlib
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class StorageBase:
    def get_site_data(self, url: str) -> Dict[str, Any]:
        raise NotImplementedError
    
    def update_site_data(self, url: str, content: str):
        raise NotImplementedError

class LocalStorage(StorageBase):
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
            "last_check": 0 
        }
        self.save()

class GCSStorage(StorageBase):
    def __init__(self, gcs_path: str):
        # Expected format: gs://bucket-name/path/to/file.json
        from google.cloud import storage
        self.client = storage.Client()
        
        path_parts = gcs_path.replace("gs://", "").split("/", 1)
        self.bucket_name = path_parts[0]
        self.blob_name = path_parts[1]
        
        self.bucket = self.client.bucket(self.bucket_name)
        self.blob = self.bucket.blob(self.blob_name)
        self.data = self._load()

    def _load(self) -> Dict[str, Any]:
        try:
            if not self.blob.exists():
                return {}
            content = self.blob.download_as_text()
            return json.loads(content)
        except Exception as e:
            logger.warning(f"Failed to load GCS data: {e}. Starting fresh.")
            return {}

    def save(self):
        try:
            self.blob.upload_from_string(json.dumps(self.data, indent=2, ensure_ascii=False))
        except Exception as e:
            logger.error(f"Failed to save to GCS: {e}")

    def get_site_data(self, url: str) -> Dict[str, Any]:
        return self.data.get(url, {})

    def update_site_data(self, url: str, content: str):
        content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
        self.data[url] = {
            "last_hash": content_hash,
            "last_content": content,
            "last_check": 0
        }
        self.save()

def get_storage(path: str) -> StorageBase:
    if path.startswith("gs://"):
        return GCSStorage(path)
    return LocalStorage(path)

# Backwards compatibility alias if needed, or update main.py to use get_storage
Storage = get_storage
