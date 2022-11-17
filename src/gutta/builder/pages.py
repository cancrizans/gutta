import jinja2
import markdown
import os
from .exceptions import TemplateNotFound

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__),'templates')

environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(TEMPLATE_DIR)
    )
templates = {
    'base':environment.get_template("base.jinja"),
    'gallery':environment.get_template("gallery.jinja"),
    'gallery_inner':environment.get_template("gallery_inner.jinja"),
    'scroll':environment.get_template('scroll.jinja'),
    'scroll_inner':environment.get_template('scroll_inner.jinja'),
    'trickle_inner':environment.get_template('trickle_inner.jinja')
}

def mdown(src:str)->str:
    return markdown.markdown(src)

def render_page(template_name:str,options:dict):
    try:
        template = templates[template_name]
    except KeyError:
        raise TemplateNotFound
    return template.render(options)