import logging
import yaml


class Configuration:
    conf = None

    def __init__(self):
        try:
            logging.debug('Loading conf file')
            file = open('cpmAws.yaml', 'r')
            self.conf = yaml.load(file)
        except():
            logging.error('Impossible to load conf. Abort')
            exit(1)

    def get(self, attr):
        return self.conf[attr]
