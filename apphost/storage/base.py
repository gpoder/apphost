from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class StorageAdapter(ABC):
    @abstractmethod
    def list_apps(self) -> List[Dict[str, Any]]:
        ...

    @abstractmethod
    def get_app(self, slug: str) -> Optional[Dict[str, Any]]:
        ...

    @abstractmethod
    def save_app(self, app_data: Dict[str, Any]) -> None:
        ...

    @abstractmethod
    def delete_app(self, slug: str) -> None:
        ...
