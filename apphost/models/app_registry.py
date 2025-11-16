
import os
from ..storage.flatfile import FlatFileStorage

def storage():
    base=os.environ.get("APPHOST_DATA_DIR","/opt/apphost/data")
    return FlatFileStorage(base)

def list_apps(): return storage().list_apps()
def get_app(slug): return storage().get_app(slug)
def create_or_update_app(slug,name,desc=""):
    storage().save_app({"slug":slug,"name":name,"description":desc})
def delete_app(slug): storage().delete_app(slug)
