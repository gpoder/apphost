import json
import os
import threading
from typing import List, Dict, Any, Optional
from .base import StorageAdapter

class FlatFileStorage(StorageAdapter):
    """Simple JSON flat-file storage for app registry."""

    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self.file_path = os.path.join(base_dir, "apps.json")
        os.makedirs(self.base_dir, exist_ok=True)
        self._lock = threading.Lock()
        if not os.path.exists(self.file_path):
            self._write({"apps": []})

    def _read(self) -> Dict[str, Any]:
        with self._lock:
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (IOError, json.JSONDecodeError):
                return {"apps": []}

    def _write(self, data: Dict[str, Any]) -> None:
        with self._lock:
            tmp = self.file_path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            os.replace(tmp, self.file_path)

    def list_apps(self) -> List[Dict[str, Any]]:
        return self._read().get("apps", [])

    def get_app(self, slug: str) -> Optional[Dict[str, Any]]:
        return next((a for a in self.list_apps() if a.get("slug") == slug), None)

    def save_app(self, app_data: Dict[str, Any]) -> None:
        data = self._read()
        apps = [a for a in data.get("apps", []) if a.get("slug") != app_data.get("slug")]
        apps.append(app_data)
        data["apps"] = sorted(apps, key=lambda x: x.get("slug", ""))
        self._write(data)

    def delete_app(self, slug: str) -> None:
        data = self._read()
        data["apps"] = [a for a in data.get("apps", []) if a.get("slug") != slug]
        self._write(data)
