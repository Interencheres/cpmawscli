from six import iteritems


class Parameters(object):
    def __init__(self, argparse):
        self.parameters = argparse
        self.tags = list()
        if self.parameters.tag:
            self._build_tags(self.parameters.tag)

    def __getattr__(self, key):
        if key == 'tag':
            return self.tags
        else:
            return getattr(self.parameters, key)

    def _build_tags(self, parameters):
        """Builds a dictionnary matching what AWS API is expecting to filter on:

        Example:
            [{
                'Name': 'tag:filtername',
                'Values': [
                    'first value',
                    'second value',
                    ...
                ]
            }, {
                ...
            }]
        """
        filters = dict()
        for name, value in parameters:
            name = "tag:{}".format(name)
            if name in filters:
                filters[name].append(value)
            else:
                filters[name] = [value]

        for name, values in iteritems(filters):
            self.tags.append({
                'Name': name,
                'Values': values
            })
