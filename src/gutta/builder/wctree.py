
import pathlib
import json
from functools import cached_property,lru_cache

from . import style,resources,assets,localpaths,dates
from .wcnode import WCNode
from .extras import ExtraPage
from .specs import read_yaml,getopt
from .feeds import Feed
from .exceptions import UnknownHierarchyLevel
from .mountpoints import MountDepot
from .blobs import Blob


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
        spinner_src = getopt(config,'loading_spinner','')
        self.spinner = assets.ImageAsset.get(spinner_src)


        self.mounts = MountDepot()

        hierarchy_spec : dict = getopt(config,'hierarchy')
        self.levels = {hid:HierarchyLevel(spec) for hid,spec in hierarchy_spec.items()}
        self.root = WCNode(None,'root',getopt(config,'root'),self,0)
        
        

        self.leaves = self.root._subordinate_leaves
        self.first = self.leaves[0]
        self.latest = self.leaves[-1]


        navbar_spec = getopt(config,'navbar',False)
        self.navbar = None
        if navbar_spec:
            self.navbar = {
                'brand_icon': assets.ImageAsset.get(getopt(navbar_spec,'brand_icon','')).path,
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

        self.webroot = getopt(config,'webroot',"[You forgot to specify a webroot]")
        self.create_feeds = getopt(config,'feed',False)
        if self.create_feeds:
            feed_entries_level_name = getopt(self.create_feeds,'entries')
            self.feed_entries_depth = self.get_depth_by_level_name(feed_entries_level_name)
            self.feed_entries = self.depth_node_map[self.feed_entries_depth]
            # print(self.all_nodes)
            # print(self.feed_entries_depth)
            # print(self.depth_node_map)

            self.feed = Feed(self.feed_entries,self.webroot,{'title':self.webcomic_title,'description':self.root.description.plaintext})

        self.ganalytics = getopt(config,'google.analytics',False)
        if self.ganalytics:
            self.ganalytics_id = getopt(self.ganalytics,'tracking_id')

        self.cactus = getopt(config,'cactus',False)
        if self.cactus:
            self.cactus_site_name = getopt(self.cactus,'site_name')

        self.labels : dict[str,Blob] = {}
        labels = getopt(config,'labels',{})
        for label_key, default in [
                ('goto_next','Continue reading: {{next.full_title}}'),
                ('end',"You've reached the end of this Webcomic - stay tuned for the next episode! [Back Home]({{sroot}})"),
                ('goto_back', "Go back to {{previous.full_title}}")
            ]:
            self.labels[label_key] = Blob(getopt(labels,label_key,default))
        

    @lru_cache
    def get_level_by_depth(self,depth:int)-> HierarchyLevel:
        return list(self.levels.values())[depth]

    @lru_cache
    def get_depth_by_level_name(self,name:str)->int:
        for i,key in enumerate(self.levels.keys()):
            if key == name:
                return i
        raise UnknownHierarchyLevel(name)

    @cached_property
    def all_nodes(self) -> list[WCNode]:
        return [self.root] + self.root._all_children

    @cached_property
    def depth_node_map(self)->dict[int,WCNode]:         
        depth_node_map : dict[int,WCNode] = {}
        for i in range(len(self.levels)):
            depth_node_map[i] = []
        for node in self.all_nodes:
            depth_node_map[node.level].append(node)
        return depth_node_map
        
        
    def parse_address(self,address:str)-> str:
        address = address.strip()
        if address.startswith('gutta.'):
            _, param = address.split('.',maxsplit=1)
            try:
                return {
                    'home':'index.html',
                    'first':self.first.url,
                    'latest':self.latest.url,
                    'rss':'rss.xml',
                    'atom':'atom.xml'
                }[param]
            except KeyError:
                print(f"I don't know what to make of '{address}'...")
                return "404.html"
        elif address.startswith("extras."):
            _,param = address.split('.',maxsplit=1)
            return param+".html"
        elif address.startswith("href."):
            _,param = address.split('.',maxsplit=1)
            return param
        else:
            return address

    def build_style(self):
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


    def dump_debug(self):
        pathlib.Path(localpaths.DEBUG).mkdir(exist_ok=True)
        
        debugs = {}
        for node in self.all_nodes:
            debugs[node.npath] = node.variables
        with open(localpaths.debugpath('variables.json'),'w') as f:
            f.write(json.dumps(debugs)) 

        mounts = []
        for node in self.all_nodes:
            if not node.do_mount:
                mountkind = f"(unmounted)"
            elif node.do_mount == 'redirect':
                mountkind = f"-> {node.url} >>> {node.unmounted_url}"
            else:
                mountkind = f"-> {node.url}"
            mounts.append(f"{node.npath} {mountkind}")
            
        with open(localpaths.debugpath('mounts.txt'),'w') as f:
            f.write("\n".join(mounts))

        with open(localpaths.debugpath('buildlist.json'),'w') as f:
            dalist = self.all_mountpoints()
            dalist += [".debug","static","index.html","rss.xml","atom.xml"]
            for page in self.extra_pages:
                dalist.append(page.name+'.html')
            json.dump(dalist,f)

    def all_mountpoints(self)->list[str]:
        return [node.url for node in self.all_nodes if node.do_mount and node.url ]
    

    def build(self):
        pathlib.Path('.nojekyll').touch()
        pathlib.Path(localpaths.STATIC).mkdir(exist_ok=True)
        for resource in ['gutta_logo_icon.svg','gutta_logo24.png']:
            resources.move_resource(resource,localpaths.STATIC)
        
        self.build_style()
        self.root.build()
        [ex.build() for ex in self.extra_pages]
        if self.create_feeds:
            self.feed.build()

        self.dump_debug()