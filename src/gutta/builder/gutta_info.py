import os
with open(os.path.join(os.path.dirname(__file__),'../VERSION'),'r') as vf:
    __version__ = vf.read().strip()

gutta_info = {
        'version': __version__
    }