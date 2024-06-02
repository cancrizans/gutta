from abc import ABC,abstractmethod

class Address(ABC):
    @abstractmethod
    def to_dict(self)->dict:
        pass

class RelativeAddress(Address):
    def __init__(self, path:str):
        self.path = path
    def to_dict(self) -> dict:
        return dict(
            kind = 'relative',
            path = self.path
        )

class AbsoluteAddress(Address):
    def __init__(self, url) -> None:
        self.url = url
    def to_dict(self) -> dict:
        return dict(
            kind = 'absolute',
            url = self.url
        )