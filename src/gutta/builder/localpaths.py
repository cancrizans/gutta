import posixpath,os
SRC = "_source"
def srcpath(p:str)->str:
    return posixpath.join(SRC,p)
ROOT_SPECFILE_PATH = srcpath("webcomic.yaml")
ASSETS = "_assets"
def assetpath(p:str)->os.path:
    return posixpath.join(ASSETS,p)
STATIC = "static"
def staticpath(p:str)->os.path:
    return posixpath.join(STATIC,p)