
import posixpath,pathlib
import oyaml as yaml
from .exceptions import MissingOption,YAMLParsingError,MissingSpecFile,NotIdentifier
from . import pages

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


SRC = "source"
def srcpath(p:str)->str:
    return posixpath.join(SRC,p)
ROOT_SPECFILE_PATH = srcpath("webcomic.yaml")

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
        if not self.nid.isidentifier():
            raise NotIdentifier(f"The node id '{self.nid}' is invalid. This is not the title, the node id should be a simple identifier")
        self.parent = parent
        if parent == None:
            self.base = ""
            self.level = 0
        else:
            self.base = parent.base + nid + "/"
            self.level = parent.level + 1
        config = list(tree.levels.values())[self.level].enrich(config)
        
        self.title = getopt(config,'title', "Empty Title")        
        self.description = getopt(config,'description',"Empty Description")
        self.children_specs = getopt(config,'children',{})
        self.children = [WCNode(self,key,spec,tree) for key,spec in self.children_specs.items()]

        self.layout = getopt(config,'layout')

        

    @property
    def nodemap(self)->dict:
        nmap = {self.base:self}
        for c in self.children:
            nmap.update(c.nodemap)
        return nmap

    def build(self):
        for child in self.children:
            child.build()

        dir = self.base
        pathlib.Path(dir).mkdir(exist_ok=True)
        page_path = posixpath.join(dir,'index.html')
        variables = {
            'title':self.title,
            'description':self.description
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
        with open(page_path,'w') as f:
            f.write(pages.render_page(self.layout,variables))



class WCTree:
    def __init__(self):
        config = read_yaml(ROOT_SPECFILE_PATH)
        hierarchy_spec = getopt(config,'hierarchy')
        self.levels = {hid:HierarchyLevel(spec) for hid,spec in hierarchy_spec.items()}
        self.root = WCNode(None,'root',getopt(config,'root'),self)
        self.nodemap : dict[str,WCNode] = self.root.nodemap
        

    def build(self):
        self.root.build()
