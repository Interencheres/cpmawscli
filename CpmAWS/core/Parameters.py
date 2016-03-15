class Parameters:
    def __init__(self,argparse):
        self.parameters=argparse
        self.tags = {}
        # tags are input in arrays, lets convert it to dict like for Tag module
        for tag in self.parameters.tag:
            self.tags[tag[0]] = tag[1]

    def __getattr__(self, key):
        if key == 'tag':
            return self.tags
        else:
            return getattr(self.parameters,key)
