from abc import ABC, abstractmethod
from src.domain.entities import Issue

class IIssueCreator(ABC):
    @abstractmethod
    async def create(self, system: str, issue: Issue) -> str:
        pass
