
import posixpath,pathlib
import oyaml as yaml
from .exceptions import MissingOption,YAMLParsingError,MissingSpecFile,NotIdentifier,EmptyTrickle
from . import pages
from functools import cached_property,lru_cache
from . import style,resources,assets,localpaths


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
    def __init__(self,parent,nid:str,config:dict,tree,index_in_parent:int):

        # Basic setup
        self.tree = tree
        self.nid = nid
        if (not self.nid.isidentifier()) or (self.nid[0]=='_'):
            raise NotIdentifier(f"The node id '{self.nid}' is invalid. This is not the title, the node id should be a simple identifier")
        if (self.nid in ["static"]):
            raise NotIdentifier(f"The node id '{self.nid}' is a reserved keyword and it's not valid. Choose something else!")
        self.title = getopt(config,'title', "Empty Title")        
        

        # Parenting and inheritance
        self.parent = parent
        if parent == None:
            self.base = ""
            self.level = 0
            self.siteroot = ""
            self.full_title = self.title
            self.prefix = getopt(config,'prefix',"")
        else:
            self.base = parent.base + nid + "/"
            self.level = parent.level + 1
            self.siteroot = parent.siteroot + "/../"
            self.full_title = parent.full_title + " - " + self.title
            
            try:
                self.prefix = getopt(config,'prefix')
            except MissingOption:
                self.prefix = parent.prefix

        self.assets_path = self.siteroot + "_assets/"
        self.static_path = self.siteroot + "static/"


        # Enrich with level data
        config = list(tree.levels.values())[self.level].enrich(config)
        
        
        # Description and text
        self.description = getopt(config,'description',"Empty Description")

        # Images

        pix = map(lambda p:p.strip(), getopt(config,'pix',"").split(','))
        pix = list(filter(None,pix))
        
        self.pix = [assets.ImageAsset.get(self.asset_pfx(pic)) for pic in pix]
        thumb_path = getopt(config,'thumb',default="")
        if thumb_path == "":
            self.thumb = assets.ImageAsset.get("nothumb.png")
        else:
            self.thumb = assets.ImageAsset.get(self.asset_pfx(thumb_path))


        # Children
        self.children_specs = getopt(config,'children',{})
        self.children = [WCNode(self,key,spec,tree,i) for i,(key,spec) in enumerate(self.children_specs.items())]

        # Mounting, layout, URL
        self.layout = getopt(config,'layout')
        self.mount = getopt(config,'mount', self.layout != "trickle")
        self.url = self.base
        if self.layout == 'trickle':
            if len(self.children) == 0:
                raise EmptyTrickle(self.nid, self.title)
            self.url = self.resolve().url
        
        # Navigation
        self.navigation = getopt(config,'nav',False)
        self.index_in_parent = index_in_parent
        
        
    def asset_pfx(self, assetpath:str)->str:
        return self.prefix+assetpath

    @property
    def nodemap(self)->dict:
        nmap = {self.base:self}
        for c in self.children:
            nmap.update(c.nodemap)
        return nmap

    @lru_cache
    def resolve(self):
        if self.layout == "trickle":
            return self.children[0]
        else:
            return self

    @cached_property
    def next_node(self):
        if self.parent:
            if len(self.parent.children)>1+self.index_in_parent:
                return self.parent.children[self.index_in_parent+1].resolve()
            else:
                return self.parent.next_node
        else:
            return 'latest'

    @cached_property
    def variables(self)->dict:
        variables = {
            'title':self.title,
            'description':pages.mdown(self.description),
            'assets':self.assets_path,
            'sroot':self.siteroot,
            'static':self.static_path,
            'full_title':self.full_title,

            

            'thumb':self.thumb.vars
        }
        if self.tree.navbar:
            variables['navbar'] = self.tree.navbar
        if self.layout == 'gallery':
            variables['entries'] = [
                {
                    'base': c.base,
                    'url': c.url,
                    'title': c.title,
                    'description': c.description,
                    'thumb': c.thumb.vars
                }
                for c in self.children
            ]
        if self.layout == 'scroll':
            variables['pix'] = [pic.vars for pic in self.pix]
            variables['entries'] = [
                {
                    "innerbody":c.innerbody 
                }
                for c in self.children   
            ]
            if self.navigation == "next":
                next = self.next_node
                if next == 'latest':
                    variables['is_latest'] = True
                else:
                    variables['navigation_destination'] = {
                        'url': next.url,
                        'title': next.title
                    }
        return variables


    @cached_property
    def body(self)->str:
        vars = {'innerbody':self.innerbody}
        vars.update(self.variables)
        return pages.render_page(self.layout,vars)

    @cached_property
    def page(self)->str:
        vars =  {'body':self.body}
        vars.update(self.variables)
        return pages.render_page('base',vars)

    @cached_property
    def innerbody(self)->str:
        return pages.render_page(self.layout + "_inner", self.variables)

    def build(self):
        dir = self.base
        pathlib.Path(dir).mkdir(exist_ok=True)
        for child in self.children:
            child.build()
        
        if self.mount:
            page_path = posixpath.join(dir,'index.html')
            with open(page_path,'w') as f:
                f.write(self.page)





class WCTree:
    def __init__(self):
        config = read_yaml(localpaths.ROOT_SPECFILE_PATH)


        hierarchy_spec = getopt(config,'hierarchy')
        self.levels = {hid:HierarchyLevel(spec) for hid,spec in hierarchy_spec.items()}
        self.root = WCNode(None,'root',getopt(config,'root'),self,0)
        self.nodemap : dict[str,WCNode] = self.root.nodemap


        navbar_spec = getopt(config,'navbar',False)
        self.navbar = None
        if navbar_spec:
            self.navbar = {
                'brand_icon': assets.ImageAsset.get(getopt(navbar_spec,'brand_icon','noicon.png')).reference,
                'brand_text': getopt(navbar_spec,'brand_text',"")
            }
            self.navbar['entries'] = [
                {'label':entry_label,'dest':self.parse_address(entry_dest)}
                for entry_label, entry_dest in getopt(navbar_spec,'menu',{}).items()
                ]
                
        
    def parse_address(self,address:str)-> str:
        address = address.strip()
        if '.' in address:
            protocol, param = address.split('.')
            if protocol == 'gutta':
                if param == 'home':
                    return ""
                elif param == 'latest':
                    return "latest"
                else:
                    return "404.html"
            elif protocol == "extras":
                return param+".html"
        else:
            return address
            

    def build(self):
        pathlib.Path('.nojekyll').touch()

        pathlib.Path(localpaths.STATIC).mkdir(exist_ok=True)

        style_gutta = resources.read_resource('gutta.scss')

        try:
            style_vars = open(localpaths.srcpath('vars.scss'),'r').read()
        except FileNotFoundError:
            style_vars = ""

        try:
            style_overrides = open(localpaths.srcpath('style.scss'),'r').read()
        except FileNotFoundError:
            style_overrides = ""

        compiled_css = style.build_style([style_vars,style_gutta,style_overrides])

        with open(localpaths.staticpath('wc.css'),'w') as f:
            f.write(compiled_css)

        self.root.build()
