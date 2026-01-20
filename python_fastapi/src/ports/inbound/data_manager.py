from abc import ABC, abstractmethod

class DataManager(ABC):
    @abstractmethod
    async def process(
        self,
        operation: str,
        entity: str,
        **kwargs
        ): ...