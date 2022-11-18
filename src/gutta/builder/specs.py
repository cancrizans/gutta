
import oyaml as yaml
from .exceptions import MissingOption,YAMLParsingError,MissingSpecFile


def read_yaml(path):
    try:
        with open(path,'r') as stream:
            try:
                return yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
                raise YAMLParsingError(exc)
    except FileNotFoundError:
        raise MissingSpecFile(path)



def getopt(config:dict, key:str, default = None):
    if key in config:
        return config[key]
    else:
        if default != None:
            return default
        else:
            raise MissingOption(f"Required option '{key}' is missing.")