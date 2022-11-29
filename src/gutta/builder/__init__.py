from . import wctree
import click
import os
from distutils.dir_util import copy_tree
import pathlib
import json
from . import localpaths
import errno, os, stat, shutil

def handleRemoveReadonly(func, path, exc):
  excvalue = exc[1]
  if func in (os.rmdir, os.remove) and excvalue.errno == errno.EACCES:
      os.chmod(path, stat.S_IRWXU| stat.S_IRWXG| stat.S_IRWXO) # 0777
      func(path)
  else:
      raise

def rmdir(directory):
    directory = pathlib.Path(directory)
    for item in directory.iterdir():
        if item.is_dir():
            rmdir(item)
        else:
            item.unlink()
    directory.rmdir()



def build_website():
    wc = wctree.WCTree()
    wc.build()


def create_website():
    if len(os.listdir(os.getcwd()))>0:
        print(os.listdir(os.getcwd()))
        click.echo("The current folder is not empty! Cannot setup template website.",err=True)
        return False
    
    click.echo("Assembling template webcomic...")
    from_dir = os.path.join(os.path.dirname(__file__),'../sample_comic')
    to_dir = os.getcwd()
    copy_tree(from_dir,to_dir)

    pathlib.Path('_assets').mkdir(exist_ok=True)

    click.echo("Done!")
    return


def clean_website():
    if pathlib.Path('_source/webcomic.yaml').is_file():
        # for item in os.listdir(os.getcwd()):
        #     if not item.startswith("_"):
        #         print(f"Delete {item}")
        try:
            dalist = json.load(open(localpaths.debugpath('buildlist.json'),'r'))
        except FileNotFoundError:
            click.echo("No buildlist.json file found... looks like you'll have to clean by hand.")
            return
        for item in dalist:
            print(f"Delete {item}")
            path = pathlib.Path(item)
            if path.is_dir():
                shutil.rmtree(item,ignore_errors=False,onerror=handleRemoveReadonly)
            elif path.is_file():
                os.remove(path)
            else:
                pass
            # if path.is_dir():
            #     rmdir(path)
            # elif path.is_file():
            #     path.unlink()
            # else:
            #     click.echo("???")

        click.echo("Done!")
    else:
        click.echo("Can't find webcomic.yaml! Is this even the right folder?",err=True)