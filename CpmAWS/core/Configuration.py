import logging
import yaml


class Configuration:
    conf = None

    def __init__(self):
        try:
            logging.debug('Loading conf file')
            handle = open('cpmAws.yaml', 'r')
            self.conf = yaml.load(handle)
        except Exception:
            logging.error('Impossible to load conf. Abort')
            exit(1)

    def get(self, attr):
        return self.conf[attr]
