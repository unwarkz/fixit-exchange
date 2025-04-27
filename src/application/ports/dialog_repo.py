from abc import ABC, abstractmethod
from src.domain.entities import Dialog

class IDialogRepository(ABC):
    @abstractmethod
    def get(self, user_id: str) -> Dialog:
        pass

    @abstractmethod
    def save(self, dialog: Dialog):
        pass
