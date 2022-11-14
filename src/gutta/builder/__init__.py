from . import wctree
import click
import os
from distutils.dir_util import copy_tree

import pathlib

def build_website():
    wc = wctree.WCTree()
    wc.build()


def create_website():
    if len(os.listdir(os.getcwd()))>0:
        print(os.listdir(os.getcwd()))
        click.echo("The current folder is not empty! Cannot setup template website.",err=True)
        return False
    
    click.echo("Assembling template webcomic...")
    from_dir = os.path.join(os.path.dirname(__file__),'../../sample_comic')
    to_dir = os.getcwd()
    copy_tree(from_dir,to_dir)

    pathlib.Path('assets').mkdir(exist_ok=True)

    click.echo("Done!")
    return
