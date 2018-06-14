import base64
import boto3
import json
import logging
from Tags import Tags


class Aws(object):
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
        self.tagsobject = self.makeTags(self.AwsTagsGet())
        return self

    @property
    def tags(self):
        return self.tagsobject

    # to be defined in instance classes must return { 'Key': key, 'Value': value}
    def AwsTagsGet(self):
        # @TODO mettre une exception
        return None

    def makeTags(self, awstags):
        tags = Tags()
        try:
            for tag in awstags:
                tags.add(tag['Key'], tag['Value'])
        except Exception as e:
            logging.error('Error reading tags')
            logging.error(format(e))
        return tags

    def getArn(self):
        return 'arn:aws:%s:%s:%s:%s:%s' % (
            self.arnService,
            self.configuration.get('region'),
            boto3.client(
                'sts',
                aws_access_key_id=self.parameters.aws_access_key_id,
                aws_secret_access_key=self.parameters.aws_secret_access_key
            ).get_caller_identity()["Account"],
            self.arnType,
            self.awsObject[self.arnPropertyForId]
        )

    def get(self, awsProperty):
        if awsProperty in self.awsObject:
            return self.awsObject[awsProperty]
        return None

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

    @property
    def tagPrefix(self):
        return self.arnType + self.arnService + '_'

    def decodeTags(self, awsObject):
        # concatenate all the tags
        i = 0
        encodedtags = ""
        while self.tags.get(str(awsObject.tagPrefix) + str(i)) is not False:
            encodedtags += self.tags.get(str(awsObject.tagPrefix) + str(i))
            i = i + 1
        return json.loads(base64.b64decode(encodedtags))

    def makeTagsForSnapshot(self):
        # characters are limited so base64encode the chunk
        jsonTags = json.dumps(self.getInstancePropertiesForSnapshot(self.awsObject))
        logging.debug('Tags for ' + self.id + ' ' + jsonTags)
        serialized_properties = base64.b64encode(jsonTags)
        tags = []

        # split in 256 chunks as tag values are limited to 256
        for index, chunk in enumerate(
                [serialized_properties[i:i + 256] for i in range(0, len(serialized_properties), 256)]):
            tags.append({
                'Key': self.tagPrefix + str(index),
                'Value': chunk
            })
        # snapshots are only allowed 10 tags
        if len(tags) > 10:
            logging.error('properties exceed 10 tags')
            exit(255)

        return tags

    def getInstancePropertiesForSnapshot(self, awsObject):
        id = self.arnService + self.arnType
        # Simple value Tags
        if 'Simple' in self.configuration.get('tags')[id]:
            properties = {key: value for key, value in awsObject.items() if
                          key in self.configuration.get('tags')[id]['Simple']}

        if 'Dict' in self.configuration.get('tags')[id]:
            for key, value in self.configuration.get('tags')[id]['Dict'].iteritems():
                if key in self.awsObject:
                    if value not in properties:
                        properties[value] = []
                    properties[value].append(self.get(key)[value])
                else:
                    logging.notice('Property ' + key + ' not found for ' + self.id)

        if 'Array' in self.configuration.get('tags')[id]:
            for key, value in self.configuration.get('tags')[id]['Array'].iteritems():
                if key in self.awsObject:
                    for prop in self.get(key):
                        if key not in properties:
                            properties[key] = []
                        # this is dreadful but that's the AWS API's way
                        properties[prop[value] + 's'].append(prop[value])
                else:
                    logging.notice('Property ' + key + ' not found for ' + self.id)
        # List dict Tags to simple, as RDS api is not homogeneous
        if 'DictToSimple' in self.configuration.get('tags')[id]:
            for key, value in self.configuration.get('tags')[id]['DictToSimple'].iteritems():
                properties[value] = self.get(key)[value]

        # List array Tags to simple, as RDS api is not homogeneous
        if 'ArrayToSimple' in self.configuration.get('tags')[id]:
            for key, value in self.configuration.get('tags')[id]['ArrayToSimple'].iteritems():
                # @TODO remove the [0] when snapshot creation supports list for this property
                properties[value] = self.get(key)[0][value]

        logging.debug('Properties for snapshot ' + str(properties))
        return properties
