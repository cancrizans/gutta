from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .wctree import WCTree

import posixpath,pathlib
from .exceptions import MissingOption,NotIdentifier,EmptyTrickle,UnsupportedFeature,NoChildDates,BuildError
from . import pages
from functools import cached_property,lru_cache
from . import assets
from .specs import getopt
import datetime
from . import gutta_info
from .blobs import Blob

import traceback

class WCNode:
    def __init__(self,parent : WCNode,nid:str,config:dict,tree : WCTree,index_in_parent:int):

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
        self.level : int = -1
        if parent == None:
            self.level = 0
            self.full_title = self.short_title
            self.prefix = getopt(config,'prefix',"")
            self.npath = self.nid
        else:
            self.level = parent.level + 1
            self.full_title = " - ".join([x for x in [parent.full_title, self.short_title] if x])
            self.npath = parent.npath+"."+self.nid
            try:
                self.prefix = getopt(config,'prefix')
            except MissingOption:
                self.prefix = parent.prefix

        # ===== ENRICHMENT HERE =======
        # Enrich with level data
        hlevel = tree.get_level_by_depth(self.level)
        config = hlevel.enrich(config) 

        # Mounting, Layout and URL
        self.layout = getopt(config,'layout')
        self.do_mount = getopt(config,'mount', self.layout != "trickle")
        if self.do_mount:
            self.recommended_mountpoint = getopt(config,'mountpoint',self.nid if self.parent else '')
            self.mountpoint = self.tree.mounts.beg(self.recommended_mountpoint)
            self.base = self.mountpoint.base
            self.siteroot = self.mountpoint.sroot
            self.assets_path = self.siteroot + "_assets/"
            self.static_path = self.siteroot + "static/"
        else:
            if self.parent:
                self.assets_path = self.parent.assets_path
                self.static_path = self.parent.static_path
                self.siteroot = self.parent.siteroot
            else:
                raise BuildError("The root node must be mounted. Make sure 'root' has mount:yes.")
        
        if (not self.do_mount) or self.do_mount == 'redirect':
            if self.parent:
                self.anchor = self.parent.beg_anchor(self.nid)
            else:
                raise BuildError(f"The root node's 'mount' field is '{self.do_mount}'. The root node must have mount:yes.")



        
        # Description and text
        self.description = Blob(getopt(config,'description',""))
        banner_path = getopt(config,'banner',"")
        self.banner = None
        if banner_path:
            self.banner = assets.ImageAsset.get(banner_path)

        self.show_title = getopt(config,'show_title',True)
        self.list_in_toc = getopt(config,'list_in_toc',True)
        self.infobox = getopt(config,'infobox',False)

        # Comments

        self.comments = getopt(config,'comments',False)
        if self.comments:
            self.cactus_id = self.npath.replace('_','..')

        # Images

        pix = assets.parse_pixstring(getopt(config,'pix',""))
        self.pix = [assets.ImageAsset.get(self.asset_pfx(pic)) for pic in pix]
        thumb_path = getopt(config,'thumb',default="")        
        self.thumb = assets.ImageAsset.get(self.asset_pfx(thumb_path))

        try:
            self.feed_img = assets.ImageAsset.get(self.asset_pfx(getopt(config,'feed.img')))
        except MissingOption:
            if self.thumb:
                self.feed_img = self.thumb
            elif len(self.pix)>0:
                self.feed_img = self.pix[0]
            else:
                self.feed_img = None
        
        # Opengraph inherit

        self.og_title = self.full_title
        self.og_site_name = self.tree.webcomic_title
        
        self.og_description = Blob('Webcomics!')
        if self.description:
            self.og_description = self.description
        elif (self.parent) and self.parent.description:
            self.og_description = self.parent.description
        


        # Children
        self.anchor_depot : set[str] = set()
        self.children_specs = getopt(config,'children',{})
        self.children = [WCNode(self,key,spec,tree,i) for i,(key,spec) in enumerate(self.children_specs.items())]
        self.is_leaf = len(self.children) == 0
        if self.is_leaf:
            self._subordinate_leaves = [self]
        else:
            self._subordinate_leaves = [leaf for child in self.children for leaf in child._subordinate_leaves]
        
        # Navigation
        
        self.index_in_parent = index_in_parent
        self.content_is_link = getopt(config,'content_is_link',False)

        # Date
        self.show_date = getopt(config,'show_date',False)
        self.dated = getopt(config,'dated',False)
        if self.dated:
            
            self.date_str = getopt(config,'date',"")
            if (self.date_str) and (not self.is_leaf):
                raise UnsupportedFeature(
                    ("You have a non-leaf node which is manually dated. "
                    "Currently, this is unsupported. Date its children "
                    "instead and the date range will be propagated upwards."))

        self.date : datetime.datetime = None # will be parsed/interpolated later.




        # Opengraph backflow
        try:
            self.og_img = assets.ImageAsset.get(self.asset_pfx(getopt(config,'og.img')))
        except MissingOption:
            if len(self.pix)>0:
                self.og_img = self.pix[0]
            elif self.thumb:
                self.og_img = self.thumb
            elif len(self.children)>0:
                    self.og_img = self.children[0].og_img
            else:
                self.og_img = assets.ImageAsset.get('')
        
        
        
    def asset_pfx(self, assetpath:str)->str:
        if assetpath:
            return self.prefix+assetpath
        else:
            return ""

    @property
    def nodemap(self)->dict:
        nmap = {self.base:self}
        for c in self.children:
            nmap.update(c.nodemap)
        return nmap

    @cached_property
    def _all_children(self)->dict[int,list[WCNode]]:
        return self.children + [grandchild for child in self.children for grandchild in child._all_children]

    @lru_cache
    def _resolve_direction(self,forward:bool):
        if self.layout == 'trickle':
            return self.children[0 if forward else -1]
        else:
            return self
    @lru_cache
    def resolve(self):
        return self._resolve_direction(True)
    @lru_cache
    def resolve_back(self):
        return self._resolve_direction(False)

    def beg_anchor(self,recommendation:str):
        if self.do_mount:
            if not recommendation in self.anchor_depot:
                self.anchor_depot.add(recommendation)
                return recommendation
            for l in range(200):
                digited = recommendation + str(l)
                if not digited in self.anchor_depot:
                    self.anchor_depot.add(digited)
                    return digited
            raise ValueError("Ran out of anchor space??")
        else:
            return self.parent.beg_anchor(recommendation)


    @cached_property
    def unmounted_url(self)->str:
        return self.parent.url + "#" + self.anchor

    @cached_property
    def url(self)->str:
        url = None
        if self.do_mount:
            url = self.base
        if self.layout == 'trickle':
            if len(self.children) == 0:
                raise EmptyTrickle(self.nid, self.title)
            url = self.resolve().url
        elif not self.do_mount:
            url = self.unmounted_url
        return url

    @lru_cache
    def permalink(self,webroot)->str:
        return webroot + self.url

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
    def previous_node(self):
        if self.parent:
            if self.index_in_parent == 0:
                return self.parent.previous_node
            else:
                return self.parent.children[self.index_in_parent-1].resolve_back()
        else:
            return 'first'

    @cached_property
    def _toc_subtree(self)->dict:
        stree = {'show': self.list_in_toc, 'title': self.title,'full_title':self.full_title, 'url': self.url}
        if self.is_leaf:
            stree['leaf'] = True
        else:
            stree['leaf'] = False
            stree['sons'] = [son._toc_subtree for son in self.children]
        return stree

    def _date_limit(self, high:bool)->datetime.datetime:
        if self.date:
            return self.date
        else:
            if self.is_leaf:
                raise NoChildDates(self.nid)
            if high:
                return max([c.date_high for c in self.children])
            else:
                return min([c.date_low for c in self.children])


    @cached_property
    def date_low(self)->datetime.datetime:
        return self._date_limit(False)
    @cached_property
    def date_high(self)->datetime.datetime:
        return self._date_limit(True)
    

    @cached_property
    def date_format(self)->str:
        if self.date:
            return self.date.strftime('%d %B, %Y')
        else:
            lowfmt = self.date_low.strftime('%B %Y')
            highfmt = self.date_high.strftime('%B %Y')
            if lowfmt == highfmt:
                return lowfmt
            else:
                return f"{lowfmt} - {highfmt}"



    @cached_property
    def variables(self)->dict:
        variables = {
            'gutta':gutta_info.gutta_info,
            'title':self.title,    
            'assets':self.assets_path,
            'sroot':self.siteroot,
            'static':self.static_path,
            'full_title':self.full_title,
            'show_title':self.show_title,
            'thumb':self.thumb.vars,
            'head_title':' - '.join([ x for x in [self.tree.webcomic_title,self.full_title] if x]),
            'favicon':self.tree.favicon.vars,
            'permalink': self.permalink(self.tree.webroot),
            
        }
        if self.tree.ganalytics:
            variables['ganalytics'] = self.tree.ganalytics
        if self.comments:
            if self.tree.cactus:
                variables['cactus'] = dict(
                    section_id = self.cactus_id,
                    site_name = self.tree.cactus_site_name
                )
            else:
                raise BuildError("Node marked to show comments, but no comments framework defined.")

        if self.do_mount:
            variables['opengraph'] = dict(
                title=self.og_title,
                site_name=self.og_site_name,
                description=self.og_description.plaintext,
                image=dict(
                    url=self.og_img.absolute_url(self.tree.webroot),
                    alt=self.og_description.plaintext,
                    width=self.og_img.image_width,
                    height=self.og_img.image_height
                )
            )

        if self.show_date:
            variables['date'] = self.date_format
        
        if self.description:
            variables['description'] = self.description.html
        if self.banner:
            variables['banner'] = self.banner.vars
        if self.tree.navbar:
            variables['navbar'] = self.tree.navbar
        if self.layout == 'gallery':
            variables['entries'] = []
            for c in self.children:
                entry = {
                    'url': c.url,
                    'title': c.title,
                    'description': c.description.html,
                    'description_plain' : c.description.plaintext,
                    'thumb': c.thumb.vars,
                    
                }
                if c.show_date:
                    entry['date'] = c.date_format
                variables['entries'].append(entry)
                
            
        if self.layout == 'scroll':
            variables['content_is_link'] = self.content_is_link
            variables['pix'] = [pic.vars for pic in self.pix]
            variables['entries'] = [
                
                 {
                    "innerbody":c.innerbody ,
                    "anchor":c.anchor
                }
               
                for c in self.children]
            
            variables['infobox'] = self.infobox
            variables['spinner'] = self.tree.spinner.vars
            
            next = self.next_node
            if next == 'latest':
                variables['is_latest'] = True
            else:
                variables['navigation_destination'] = {
                    'url': next.url,
                    'title': next.title,
                    'full_title':next.full_title
                }

            prev = self.previous_node
            if prev == 'first':
                variables['is_first'] = True
            else:
                variables['back_destination'] = {
                    'url': prev.url,
                    'title': prev.title,
                    'full_title':prev.full_title
                }

        # if self.level == 2:
        #     print(f"==={self.nid}===")
        #     print(variables)
        return variables


    @cached_property
    def body(self)->str:
        vars = {'innerbody':self.innerbody}
        vars.update(self.variables)
        return pages.render_page(self.layout,vars)

    @lru_cache
    def render_page(self,body:str)->str:
        if self.do_mount is True:
            vars =  {'body':body}
            vars.update(self.variables)
            return pages.render_page('base',vars)
        elif self.do_mount == 'redirect':
            vars = dict(redirect=self.siteroot+self.unmounted_url)
            vars.update(self.variables)
            return pages.render_page('redirect',vars)
        elif not self.do_mount:
            raise ValueError(".render_page called on an unmounted node?")
        else:
            raise BuildError(f"Unknown 'mount' value '{self.do_mount}'.")

    @cached_property
    def page(self)->str:
        return self.render_page(self.body)

    @cached_property
    def innerbody(self)->str:
        return pages.render_page(self.layout + "_inner", self.variables)

    def build(self):
        for child in self.children:
            child.build()
        
        if self.do_mount:
            try:
                self.page
            except Exception as e:
                print(f"Error while building node '{self.npath}'")
                traceback.print_exc()

            dir = self.base
            pathlib.Path(dir).mkdir(exist_ok=True)
            page_path = posixpath.join(dir,'index.html')
            with open(page_path,'w') as f:
                f.write(self.page)