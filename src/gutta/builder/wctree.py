
import posixpath,pathlib
import oyaml as yaml
from .exceptions import MissingOption,YAMLParsingError,MissingSpecFile,NotIdentifier
from . import pages
import os
from click import echo
from functools import cached_property
from . import style
from . import resources

def read_yaml(path):
    try:
        with open(path,'r') as stream:
            try:
                return yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
                raise YAMLParsingError(exc)
    except FileNotFoundError:
        raise MissingSpecFile(path)


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

def getopt(config:dict, key:str, default = None):
    if key in config:
        return config[key]
    else:
        if default != None:
            return default
        else:
            raise MissingOption(f"Required option '{key}' is missing.")

class HierarchyLevel:
    def __init__(self,spec:dict):
        self.spec = spec
    def enrich(self,otherspec:dict)->dict:
        return dict(list(self.spec.items()) + list(otherspec.items()))

class WCNode:
    def __init__(self,parent,nid:str,config:dict,tree):
        self.tree = tree
        self.nid = nid
        if (not self.nid.isidentifier()) or (self.nid[0]=='_'):
            raise NotIdentifier(f"The node id '{self.nid}' is invalid. This is not the title, the node id should be a simple identifier")
        self.title = getopt(config,'title', "Empty Title")        
        self.parent = parent
        if parent == None:
            self.base = ""
            self.level = 0
            self.siteroot = ""
            self.full_title = self.title
        else:
            self.base = parent.base + nid + "/"
            self.level = parent.level + 1
            self.siteroot = parent.siteroot + "/../"
            self.full_title = parent.full_title + " - " + self.title

        self.assets_path = self.siteroot + "_assets/"
        self.static_path = self.siteroot + "static/"

        config = list(tree.levels.values())[self.level].enrich(config)
        
        
        self.description = getopt(config,'description',"Empty Description")
        self.children_specs = getopt(config,'children',{})
        self.children = [WCNode(self,key,spec,tree) for key,spec in self.children_specs.items()]

        self.layout = getopt(config,'layout')

        pix = map(lambda p:p.strip(), getopt(config,'pix',"").split(','))
        pix = list(filter(None,pix))
        self.pix = pix

        for pic in pix:
            if not os.path.isfile(assetpath(pic)):
                echo(f"Warning: image asset {pic} was referenced but not found.")

        

    @property
    def nodemap(self)->dict:
        nmap = {self.base:self}
        for c in self.children:
            nmap.update(c.nodemap)
        return nmap

    @cached_property
    def variables(self)->dict:
        variables = {
            'title':self.title,
            'description':pages.mdown(self.description),
            'assets':self.assets_path,
            'sroot':self.siteroot,
            'static':self.static_path,
            'full_title':self.full_title
        }
        if self.layout == 'gallery':
            variables['entries'] = [
                {
                    'base': c.base,
                    'title': c.title,
                    'description': c.description
                }
                for c in self.children
            ]
        if self.layout == 'scroll':
            variables['pix'] = self.pix
            variables['entires'] = [
                {
                    "body":c.body 
                }
                for c in self.children   
            ]
        return variables


    @cached_property
    def body(self)->str:
        return pages.render_page(self.layout,self.variables)

    @cached_property
    def page(self)->str:
        vars =  {'body':self.body}
        vars.update(self.variables)
        return pages.render_page('base',vars)


    def build(self):
        for child in self.children:
            child.build()
        dir = self.base
        pathlib.Path(dir).mkdir(exist_ok=True)
        page_path = posixpath.join(dir,'index.html')
        with open(page_path,'w') as f:
            f.write(self.page)



class WCTree:
    def __init__(self):
        config = read_yaml(ROOT_SPECFILE_PATH)
        hierarchy_spec = getopt(config,'hierarchy')
        self.levels = {hid:HierarchyLevel(spec) for hid,spec in hierarchy_spec.items()}
        self.root = WCNode(None,'root',getopt(config,'root'),self)
        self.nodemap : dict[str,WCNode] = self.root.nodemap
        

    def build(self):
        pathlib.Path(STATIC).mkdir(exist_ok=True)

        style_gutta = resources.read_resource('gutta.scss')
        compiled_css = style.build_style([style_gutta])

        with open(staticpath('wc.css'),'w') as f:
            f.write(compiled_css)

        self.root.build()
