import os
import shutil

def respath(fname:str)->str:
    return os.path.join(os.path.dirname(__file__),"resources",fname)

def read_resource(fname:str)->str:
    path = respath(fname)
    return open(path,'r').read()

def move_resource(fname:str,dest:str):
    path = respath(fname)
    shutil.copyfile(path,os.path.join(dest,fname))