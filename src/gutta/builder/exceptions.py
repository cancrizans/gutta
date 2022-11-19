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
class UnknownHierarchyLevel(ParsingError):
    def __init__(self, lvl_name:str) -> None:
        super().__init__(f"The hierarchy level '{lvl_name}' is referenced, but was not defined in the hierarchy. Maybe it's a typo?")



class TemplateNotFound(BuildError):
    pass


class EmptyTrickle(BuildError):
    def __init__(self,nid:str,title:str):
        super().__init__(f"Node {nid} ({title}) is marked as trickle but it has no children.")

class BadPath(ParsingError):
    def __init__(self,path:str) -> None:
        super().__init__(f"The following referenced path is malformed: {path}")


class DatingError(BuildError):
    pass


class NoDates(DatingError):
    def __init__(self) -> None:
        super().__init__("There are leaf nodes marked as 'dated' but none of them have a date, so I cannot interpolate.")
class DateParsingFailure(DatingError):
    def __init__(self, datestr:str) -> None:
        super().__init__(f"The following date string could not be parsed as a valid date: '{datestr}'.")
class NoChildDates(DatingError):
    def __init__(self, pnid:str) -> None:
        super().__init__(f"A date was requested to node '{pnid}' which is an undated leaf. This is probably because you've toggled showing dates for parent nodes without dated children.")


class UnsupportedFeature(BuildError):
    def __init__(self, feat:str) -> None:
        super().__init__(f"Unsupported: {feat}")