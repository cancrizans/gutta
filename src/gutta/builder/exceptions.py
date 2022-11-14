import oyaml as yaml

class BuildError(Exception):
    pass
class MissingSpecFile(BuildError):
    def __init__(self,path) -> None:
        super().__init__(f"Required source webcomic file {path} not found. Are you sure you're in the right folder?")


class ParsingError(BuildError):
    pass
class YAMLParsingError(ParsingError):
    def __init__(self, yaml_err : yaml.YAMLError) -> None:
        super().__init__(f"Something wrong with this yaml file...")
class MissingOption(ParsingError):
    pass

class NotIdentifier(ParsingError):
    pass



class TemplateNotFound(BuildError):
    pass