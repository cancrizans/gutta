import markdown
from functools import cached_property
from markdown import Markdown
from io import StringIO

# from https://stackoverflow.com/questions/761824/python-how-to-convert-markdown-formatted-text-to-text
def unmark_element(element, stream=None):
    if stream is None:
        stream = StringIO()
    if element.text:
        stream.write(element.text)
    for sub in element:
        unmark_element(sub, stream)
    if element.tail:
        stream.write(element.tail)
    return stream.getvalue()

Markdown.output_formats["plain"] = unmark_element
plainmd = Markdown(output_format="plain")
plainmd.stripTopLevelTags = False


class Blob:
    def __init__(self,source:str):
        self.source = source

    @cached_property
    def html(self)->str:
        rdr = markdown.markdown(self.source)
        return rdr

    @cached_property
    def plaintext(self)->str:
        return plainmd.convert(self.source)

    def __bool__(self):
        return self.source != ''