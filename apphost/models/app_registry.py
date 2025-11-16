import os
from typing import List, Dict, Any, Optional
from ..storage.flatfile import FlatFileStorage

def get_storage() -> FlatFileStorage:
    base_dir = os.environ.get("APPHOST_DATA_DIR", "/opt/apphost/data")
    return FlatFileStorage(base_dir)

def list_apps() -> List[Dict[str, Any]]:
    return get_storage().list_apps()

def get_app(slug: str) -> Optional[Dict[str, Any]]:
    return get_storage().get_app(slug)

def create_or_update_app(slug: str, name: str, description: str = "") -> Dict[str, Any]:
    app_data = {
        "slug": slug,
        "name": name,
        "description": description,
    }
    storage = get_storage()
    storage.save_app(app_data)
    return app_data

def delete_app(slug: str) -> None:
    get_storage().delete_app(slug)
