from .wcnode import WCNode
from feedgen.feed import FeedGenerator
import pytz
from functools import cached_property

class Feed:
    def __init__(self, entries: list[WCNode], webroot:str, metadata:dict) -> None:
        self.entries = entries
        self.webroot = webroot
        self.metadata = metadata

    @cached_property
    def generator(self)->FeedGenerator:
        fg = FeedGenerator()
        fg.title(self.metadata['title'])
        fg.description(self.metadata['description'])
        fg.link(dict(href=self.webroot,rel='alternate'))
        fg.id(self.webroot)

        for entry in self.entries:
            fe = fg.add_entry()
            permalink = entry.permalink(self.webroot)
            fe.id(permalink)
            fe.title(entry.full_title)
            fe.link(dict(href=permalink,rel='alternate'))

            pic = entry.feed_img
            desc = f"<img src='{pic.absolute_url(self.webroot)}' width='{pic.image_width}' height='{pic.image_height}' alt='{entry.full_title}'></hr>{entry.description}"
            fe.description(desc)
            fe.published(pytz.utc.localize(entry.date))
        
        
        return fg

    @cached_property
    def rss(self)->str:
        return self.generator.rss_str(pretty=True).decode('utf-8')
    @cached_property
    def atom(self)->str:
        return self.generator.atom_str(pretty=True).decode('utf-8')

    def build(self):
        with open('rss.xml','w') as rss_f:
            rss_f.write(self.rss)
        with open('atom.xml','w') as atom_f:
            atom_f.write(self.atom)