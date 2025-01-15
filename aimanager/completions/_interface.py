from abc import ABC, abstractmethod


class CompletionProviderInterface(ABC):

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.init_client(*args, **kwargs)

    @abstractmethod
    def init_client(self, *args, **kwargs) -> dict:
        pass

    @abstractmethod
    def generate_response(self, messages: list = None, model: str = None, stream: bool = False) -> str:
        pass
