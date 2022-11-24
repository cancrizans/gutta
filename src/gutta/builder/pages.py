import jinja2
import markdown
import os
from .exceptions import TemplateNotFound

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__),'templates')

environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(TEMPLATE_DIR),
    trim_blocks=True,
    lstrip_blocks=True
    )

class Template:
    def __init__(self, tname:str, full_page:bool):
        self.tname = tname
        self.full_page = full_page
        self._template = environment.get_template(f"{tname}.jinja")

    def render(self,options:dict)-> str:
        rdr = self._template.render(options)
        if self.full_page:
            rdr = rdr.replace('__GUTTA_LAZY_LOAD','eager',1)
            rdr = rdr.replace('__GUTTA_LAZY_LOAD','lazy')
        return rdr

templates_list = [
    Template('base',True),
    Template('gallery',True),
    Template('gallery_inner',False),
    Template('scroll',True),
    Template('scroll_inner',False),
    Template('trickle_inner',False),
    Template('toc_inner',False),
    Template('extra',True),
    Template('redirect',True)
]

templates = {t.tname : t for t in templates_list}


def render_page(template_name:str,options:dict):
    try:
        template = templates[template_name]
    except KeyError:
        raise TemplateNotFound
    return template.render(options)    
    
