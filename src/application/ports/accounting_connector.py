from abc import ABC, abstractmethod
from typing import List
from src.domain.entities import DomainEvent

class IAccountingConnector(ABC):
    @abstractmethod
    async def fetch_payment_statuses(self) -> List[dict]:
        pass

    @abstractmethod
    async def send_issue_update(self, updates: List[dict]):
        pass
