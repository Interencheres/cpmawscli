import boto3
import logging
from Tags import Tags

class Aws:
    configuration = None
    parameters = None
    aws = None
    awsObject = None
    arnService = 'to override'
    arnType = 'to override'
    arnPropertyForId = 'to override'
    tagsobject = None

    def __init__(self, orchestrator, aws=None):
        self.orchestrator = orchestrator
        self.configuration = orchestrator.configuration
        self.parameters = orchestrator.parameters
        self.aws = aws


    def load(self, awsObject):
        self.awsObject = awsObject
        self.tagsobject=self.makeTags(self.AwsTagsGet())
        return self

    @property
    def tags(self):
        return self.tagsobject

    # to be defined in instance classes must return { 'Key': key, 'Value': value}
    def AwsTagsGet(self):
        #@TODO mettre une exception
        return None

    def makeTags(self,awstags):
        object=Tags()
        try:
            for tag in awstags:
                object.add(tag['Key'],tag['Value'])
        except Exception as e:
            logging.notice('Error reading tags')
            logging.error(format(e))
        return object

    def getArn(self):
        return 'arn:aws:%s:%s:%s:%s:%s' % (
            self.arnService,
            self.configuration.get('region'),
            boto3.client(
                'iam',
                aws_access_key_id=self.parameters.aws_access_key_id,
                aws_secret_access_key=self.parameters.aws_secret_access_key
            ).get_user()['User']['Arn'].split(':')[4],
            self.arnType,
            self.awsObject[self.arnPropertyForId]
        )

    def get(self, awsProperty):
        return self.awsObject[awsProperty]

    # id used for arn
    @property
    def id(self):
        return self.get(self.arnPropertyForId)

    # name used by human, defaults to id like RDS but can be overridden
    @property
    def name(self):
        return self.id

    def connect(self):
        logging.notice("Connecting to region " + self.configuration.get('region') + "...")
        try:
            if self.parameters.aws_access_key_id and self.parameters.aws_secret_access_key:
                self.aws = boto3.client(self.arnService, self.configuration.get('region'),
                                    aws_access_key_id=self.parameters.aws_access_key_id,
                                    aws_secret_access_key=self.parameters.aws_secret_access_key)
            else:
                self.aws = boto3.client(self.arnService, self.configuration.get('region'))
            logging.notice("Connected to region " + self.configuration.get('region'))
            return self.aws
        except Exception as e:
            logging.error(format(e))
        return False


