
import pathlib
from . import style,resources,assets,localpaths,dates
from .wcnode import WCNode
from .extras import ExtraPage
from .specs import read_yaml,getopt


class HierarchyLevel:
    def __init__(self,spec:dict):
        self.spec = spec
    def enrich(self,otherspec:dict)->dict:
        return dict(list(self.spec.items()) + list(otherspec.items()))


class WCTree:
    def __init__(self):
        config = read_yaml(localpaths.ROOT_SPECFILE_PATH)

        self.webcomic_title = getopt(config,'title',"My Webcomic")
        favicon_src = getopt(config,'favicon','favicon.ico')
        self.favicon = assets.ImageAsset.get(favicon_src)

        hierarchy_spec = getopt(config,'hierarchy')
        self.levels = {hid:HierarchyLevel(spec) for hid,spec in hierarchy_spec.items()}
        self.root = WCNode(None,'root',getopt(config,'root'),self,0)
        self.nodemap : dict[str,WCNode] = self.root.nodemap
        self.leaves = self.root._subordinate_leaves
        self.latest = self.leaves[-1]


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

        self.extra_pages = [ExtraPage(spec,self.root,name) for name,spec in getopt(config,'extras',{}).items()]
        
        self.dated_leaves = [leaf for leaf in self.leaves if leaf.dated]
        self.interpolated_dates = dates.daterpolation( [n.date_str for n in self.dated_leaves] )
        for i,leaf in enumerate(self.dated_leaves):
            leaf.date = self.interpolated_dates[i]
                
        
    def parse_address(self,address:str)-> str:
        address = address.strip()
        if '.' in address:
            protocol, param = address.split('.')
            if protocol == 'gutta':
                if param == 'home':
                    return "index.html"
                elif param == 'latest':
                    return self.latest.url
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
        [ex.build() for ex in self.extra_pages]
