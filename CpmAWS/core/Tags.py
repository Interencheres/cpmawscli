
class Tags:
    dictionnary={}

    def __init__(self):
        self.dictionnary={}

    def add(self,key,value):
        self.dictionnary[key]=value

    def get(self,key):
        if key in self.dictionnary:
            return self.dictionnary[key]
        return False

    @property
    def list(self):
        return self.dictionnary
