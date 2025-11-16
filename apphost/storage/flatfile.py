
import json, os, threading
from .base import StorageAdapter

class FlatFileStorage(StorageAdapter):
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.file = os.path.join(base_dir,"apps.json")
        os.makedirs(base_dir, exist_ok=True)
        self.lock=threading.Lock()
        if not os.path.exists(self.file):
            self._write({"apps":[]})

    def _read(self):
        try:
            with self.lock, open(self.file,"r") as f:
                return json.load(f)
        except:
            return {"apps":[]}

    def _write(self,data):
        tmp=self.file+".tmp"
        with self.lock, open(tmp,"w") as f:
            json.dump(data,f,indent=2)
        os.replace(tmp,self.file)

    def list_apps(self):
        return self._read().get("apps",[])

    def get_app(self, slug):
        return next((a for a in self.list_apps() if a.get("slug")==slug),None)

    def save_app(self,data):
        all=self._read()
        apps=[a for a in all.get("apps",[]) if a.get("slug")!=data.get("slug")]
        apps.append(data)
        all["apps"]=sorted(apps,key=lambda x:x.get("slug",""))
        self._write(all)

    def delete_app(self, slug):
        all=self._read()
        all["apps"]=[a for a in all.get("apps",[]) if a.get("slug")!=slug]
        self._write(all)
