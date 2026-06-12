from abc import ABC, abstractmethod


class Database(ABC):

    @abstractmethod
    async def connect(self):
        pass

    @abstractmethod
    async def disconnect(self):
        pass

    @abstractmethod
    async def execute(self, query: str, *args):
        pass

    @abstractmethod
    async def fetch(self, query: str, *args):
        pass
