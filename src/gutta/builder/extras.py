

from .exceptions import MissingSpecFile
from . import pages
from functools import cached_property
from . import localpaths
from .wcnode import WCNode
from .specs import getopt

class ExtraPage:
    def __init__(self,spec:dict, reference_node : WCNode, name:str) -> None:
        self.reference_node = reference_node
        self.from_src = getopt(spec,'from',"")
        self.layout = getopt(spec,'layout',"")
        self.name = name
    @cached_property
    def body(self):
        if self.from_src:
            frompath=localpaths.srcpath(self.from_src)
            try:
                with open(frompath,'r') as f:
                    source = f.read()
            except FileNotFoundError:
                raise MissingSpecFile(frompath)
            
            return pages.mdown(source)
        elif self.layout == "toc":
            return pages.render_page("toc_inner",{'toc':[self.reference_node._toc_subtree]})
        else:
            print(f"Build failed for extra page '{self.name}', unknown type")
            return pages.mdown("Unknown extra page type - Build failed")

    @cached_property
    def variables(self):
        vars = {}
        for inh in ['assets','banner','sroot','static','navbar','favicon','gutta']:
            try:
                vars[inh]=self.reference_node.variables[inh]
            except KeyError:
                pass
        vars.update({
            'title':self.name,
            "show_title":False,
            'body':self.body,
            'head_title': self.reference_node.tree.webcomic_title + " - "+ self.name
        })
        
        return vars

    @cached_property
    def page(self):
        return pages.render_page('base',self.variables)

    def build(self):
      
        with open(self.name+".html",'w') as f:
            f.write(self.page)