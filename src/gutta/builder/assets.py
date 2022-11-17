import os
from . import localpaths
from click import echo
from functools import cached_property
import imagesize
from .exceptions import BadPath


class Asset:
    _cache = {}
    @classmethod
    def get(cls,path:str):
        try:
            return cls._cache[path]
        except KeyError:
            instance = cls(path)
            cls._cache[path] = instance
            return instance

    def __init__(self,path:str):
        self.reference = path
        self.local_path = localpaths.assetpath(self.reference)
        if not os.path.isfile(self.local_path):
            echo(f"Warning: asset {self.reference} was referenced but not found.")
    
class ImageAsset(Asset):
    def __init__(self, path: str):
        super().__init__(path)
        try:
            self.image_width, self.image_height = imagesize.get(self.local_path)
        except FileNotFoundError:
            self.image_width, self.image_height = (64,64)
        except OSError:
            raise BadPath(self.local_path)

    @cached_property
    def vars(self)->dict:

        return {
            'src':self.reference,
            'width':self.image_width,
            'height':self.image_height
            }
        