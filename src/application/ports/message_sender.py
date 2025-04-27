from abc import ABC, abstractmethod

class IMessageSender(ABC):
    @abstractmethod
    async def send(self, to: str, text: str):
        pass
