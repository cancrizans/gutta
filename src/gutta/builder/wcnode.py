
import posixpath,pathlib

from .exceptions import MissingOption,NotIdentifier,EmptyTrickle,UnsupportedFeature
from . import pages
from functools import cached_property,lru_cache
from . import assets
from .specs import getopt
import datetime

class WCNode:
    def __init__(self,parent,nid:str,config:dict,tree,index_in_parent:int):

        # Basic setup
        self.tree = tree
        self.nid = nid
        if (not self.nid.isidentifier()) or (self.nid[0]=='_'):
            raise NotIdentifier(f"The node id '{self.nid}' is invalid. This is not the title, the node id should be a simple identifier")
        if (self.nid in ["static"]):
            raise NotIdentifier(f"The node id '{self.nid}' is a reserved keyword and it's not valid. Choose something else!")
        self.title = getopt(config,'title', "")        
        self.short_title = getopt(config,'short_title',self.title)
        


        # Parenting and inheritance
        self.parent = parent
        if parent == None:
            self.base = ""
            self.level = 0
            self.siteroot = ""
            self.full_title = self.short_title
            self.prefix = getopt(config,'prefix',"")

            self.npath = self.nid
        else:
            self.base = parent.base + nid + "/"
            self.level = parent.level + 1
            self.siteroot = parent.siteroot + "/../"
            self.full_title = " - ".join([x for x in [parent.full_title, self.short_title] if x])
            self.npath = parent.npath+"."+self.nid

            try:
                self.prefix = getopt(config,'prefix')
            except MissingOption:
                self.prefix = parent.prefix


        self.assets_path = self.siteroot + "_assets/"
        self.static_path = self.siteroot + "static/"


        # Enrich with level data
        config = list(tree.levels.values())[self.level].enrich(config)

        
        
        # Description and text
        self.description = getopt(config,'description',"")
        banner_path = getopt(config,'banner',"")
        self.banner = None
        if banner_path:
            self.banner = assets.ImageAsset.get(banner_path)

        self.show_title = getopt(config,'show_title',True)
        self.list_in_toc = getopt(config,'list_in_toc',True)
        self.infobox = getopt(config,'infobox',False)


        # Images

        pix = assets.parse_pixstring(getopt(config,'pix',""))
        
        self.pix = [assets.ImageAsset.get(self.asset_pfx(pic)) for pic in pix]
        thumb_path = getopt(config,'thumb',default="")
        if thumb_path == "":
            self.thumb = assets.ImageAsset.get("nothumb.png")
        else:
            self.thumb = assets.ImageAsset.get(self.asset_pfx(thumb_path))


        # Children
        self.children_specs = getopt(config,'children',{})
        self.children = [WCNode(self,key,spec,tree,i) for i,(key,spec) in enumerate(self.children_specs.items())]
        self.is_leaf = len(self.children) == 0
        if self.is_leaf:
            self._subordinate_leaves = [self]
        else:
            self._subordinate_leaves = [leaf for child in self.children for leaf in child._subordinate_leaves]


        # Mounting, layout, URL
        self.layout = getopt(config,'layout')
        self.mount = getopt(config,'mount', self.layout != "trickle")
        # url is computed on demand and cached... will it work?
        
        # Navigation
        self.navigation = getopt(config,'nav',False)
        self.index_in_parent = index_in_parent


        # Date
        self.dated = getopt(config,'dated',False)
        if self.dated:
            
            self.date_str = getopt(config,'date',"")
            if (self.date_str) and (not self.is_leaf):
                raise UnsupportedFeature(
                    ("You have a non-leaf node which is manually dated. "
                    "Currently, this is unsupported. Date its children "
                    "instead and the date range will be propagated upwards."))

        self.date : datetime.datetime = None # will be parsed/interpolated later.
        
        
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
    def url(self)->str:
        url = self.base
        if self.layout == 'trickle':
            if len(self.children) == 0:
                raise EmptyTrickle(self.nid, self.title)
            url = self.resolve().url
        elif not self.mount:
            url = self.parent.url + "#" + self.npath
        return url

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
    def _toc_subtree(self)->dict:
        stree = {'show': self.list_in_toc, 'title': self.title,'full_title':self.full_title, 'url': self.url}
        if self.is_leaf:
            stree['leaf'] = True
        else:
            stree['leaf'] = False
            stree['sons'] = [son._toc_subtree for son in self.children]
        return stree

    @cached_property
    def date_format(self)->str:
        if self.date:
            return self.date.strftime('%d %B, %Y')
        else:
            return "(no date)"

    @cached_property
    def variables(self)->dict:
        variables = {
            'title':self.title,    
            'assets':self.assets_path,
            'sroot':self.siteroot,
            'static':self.static_path,
            'full_title':self.full_title,
            'show_title':self.show_title,
            'thumb':self.thumb.vars,
            'date':self.date_format,
            'head_title':self.tree.webcomic_title + ' - '+self.full_title,
            'favicon':self.tree.favicon.vars
        }

        
        if self.description:
            variables['description'] = pages.mdown(self.description)
        if self.banner:
            variables['banner'] = self.banner.vars
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
                    "innerbody":c.innerbody ,
                    "npath":c.npath
                }
                for c in self.children   
            ]
            variables['infobox'] = self.infobox
            if self.navigation == "next":
                next = self.next_node
                if next == 'latest':
                    variables['is_latest'] = True
                else:
                    variables['navigation_destination'] = {
                        'url': next.url,
                        'title': next.title,
                        'full_title':next.full_title
                    }
        
        return variables


    @cached_property
    def body(self)->str:
        vars = {'innerbody':self.innerbody}
        vars.update(self.variables)
        return pages.render_page(self.layout,vars)

    @lru_cache
    def render_page(self,body:str)->str:
        vars =  {'body':body}
        vars.update(self.variables)
        return pages.render_page('base',vars)

    @cached_property
    def page(self)->str:
        return self.render_page(self.body)

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