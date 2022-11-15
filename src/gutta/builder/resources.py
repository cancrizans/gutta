import os

def read_resource(fname:str)->str:
    path = os.path.join(os.path.dirname(__file__),"resources",fname)
    return open(path,'r').read()