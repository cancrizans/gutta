

def validate(segment:str):
    if (not segment.isidentifier()) or (segment == 'static'):
        raise ValueError(f"String '{segment}' is not a valid mount-point segment.")



class MountPoint:
    def __init__(self,path:list[str]):
        (validate(s) for s in path)
        path = [p for p in path if p]
        self.path = path
        self.length = len(path)
        self.base = "/".join(path)+("/" if self.length>0 else '')
        self.sroot = "../"*self.length
    def __eq__(self, other):
        return (isinstance(other, self.__class__)
            and self.path == other.path)
    def __ne__(self, other):
        return not self == other
    def __hash__(self) -> int:
        return hash(self.base)
    
        
class MountDepot:
    def __init__(self):
        self._mounts : set[MountPoint] = set()

    def beg(self,recommendation:str) -> MountPoint:
        # trying as is
        minimal = MountPoint([recommendation])
        if not minimal in self._mounts:
            self._mounts.add(minimal)
            return minimal
        # with digit
        for i in range(2,200):
            digited = MountPoint([recommendation+str(i)])
            if not digited in self._mounts:
                self._mounts.add(digited)
                return digited
        # random
        # for l in range(3):
        #     ran_str = 
        #     ran = MountPoint([ran_str])
        #     if not ran in self._mounts:
        #         self._mounts.add(ran)
        #         return ran

        raise ValueError("Ran out of mount space?")
        
        
        

        



