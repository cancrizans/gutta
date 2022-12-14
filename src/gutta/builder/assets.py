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
        self.path = path
        if path:
            self.local_path = localpaths.assetpath(self.path)
            if not os.path.isfile(self.local_path):
                echo(f"Warning: asset {self.path} was referenced but not found.")
    
    def absolute_url(self,webroot:str):
        return webroot+'_assets/'+self.path

    def __bool__(self):
        return self.path != ''
    
class ImageAsset(Asset):
    def __init__(self, path: str):
        super().__init__(path)
        if path:
            try:
                self.image_width, self.image_height = imagesize.get(self.local_path)
            except FileNotFoundError:
                self.image_width, self.image_height = (64,64)
            except OSError:
                raise BadPath(self.local_path)
        else:
            self.image_width,self.image_height = 1,1

    @cached_property
    def vars(self)->dict:

        return {
            'src':self.path,
            'width':self.image_width,
            'height':self.image_height
            }
        
import re

pixstring_regex = re.compile(r"(.*)\[(\d+)-(\d+)\](.*)")


def parse_pixstring(ps:str)-> list[str]:
    pix = []

    for c in ps.split(','):
        c = c.strip()
        if c=="":
            continue
        
        m = pixstring_regex.match(c)
        if m:
            lows = m.group(2)
            highs = m.group(3)
            digs = len(lows)
            low = int(lows)
            high = int(highs)

            for i in range(low,high+1):
                pix.append(f"{m.group(1)}{str(i).zfill(digs)}{m.group(4)}")
        else:
            pix.append(c)
    return pix