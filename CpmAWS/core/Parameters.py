class Parameters:
    def __init__(self, argparse):
        self.parameters = argparse
        # tags are input in arrays, lets convert it to dict like for Tag module
        self.tags = dict(self.parameters.tag)

    def __getattr__(self, key):
        if key == 'tag':
            return self.tags
        else:
            return getattr(self.parameters, key)
