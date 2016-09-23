import CpmAWS.classes
import logging


class Collection(object):
    configuration = None
    parameters = None
    aws = None
    awsObject = None
    instanceModule = None

    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.configuration = orchestrator.configuration
        self.parameters = orchestrator.parameters

    # collection uses the connect method of the instance it's a collection of
    def connect(self):
        self.aws = getattr(getattr(CpmAWS.classes, self.instanceModule), self.instanceModule)(self.orchestrator).connect()

    # for EC2 filterring could be done on request, but for homogeneity sake, we filter afertwards as RDS doesn't support filtering on requets
    def filter(self, instancesList):
        logging.notice('Filtering instances...')
        return {
            id: instance
            for id, instance
            in instancesList.iteritems()
            if self.instanceBelongsToFilter(instance)
        }

    def instanceBelongsToFilter(self, instance):
        if self.parameters.exclude:
            for name in self.parameters.exclude:
                if instance.name == name:
                    return False

        if self.parameters.instance and (instance.name != self.parameters.instance):
            return False
        return True
