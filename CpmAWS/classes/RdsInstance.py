import base64
import json
import logging

from CpmAWS.core.Aws import Aws
from CpmAWS.core.Tags import Tags


class RdsInstance(Aws):
    # @TODO replace hash by empty object
    snapshot = {}
    arnService = 'rds'
    arnType = 'db'
    arnPropertyForId = 'DBInstanceIdentifier'

    @property
    def name(self):
        return self.id

    def AwsTagsGet(self):
        return self.aws.list_tags_for_resource(ResourceName=self.getArn())['TagList']

    def getInstancePropertiesForSnapshot(self, awsObject):
        # Simple value Tags
        properties = {key: value for key, value in awsObject.items() if
                      key in self.configuration.get('InstanceSimpleTagsForSnapshot')}

        # List dict Tags
        for key, value in self.configuration.get('InstanceDictTagsForSnapshot').iteritems():
            properties[value] = self.get(key)[value]

        # List array Tags
        for key, value in self.configuration.get('InstanceArrayTagsForSnapshot').iteritems():
            # @TODO remove the [0] when snapshot creation supports list for this property
            properties[value] = self.get(key)[0][value]

        # if multiaz remove the availability zone
        if properties['MultiAZ'] is True:
            del (properties['AvailabilityZone'])

        logging.debug('Properties for snapshot ' + str(properties))
        return properties

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
                'Key': 'instanceProperties_' + str(index),
                'Value': chunk
            })
        # snapshots are only allowed 10 tags
        if len(tags) > 10:
            logging.error('properties exceed 10 tags')
            exit(255)

        return tags

    def exist(self, DBInstanceIdentifier):
        try:
            self.aws.describe_db_instances(DBInstanceIdentifier=DBInstanceIdentifier)
        except:
            # exception if dbinstanceidentifier not found
            return False
        return True

    def delete(self):
        logging.notice('Deleting instance ' + self.id)
        try:
            output = self.aws.delete_db_instance(
                DBInstanceIdentifier=self.id,
                SkipFinalSnapshot=True
            )
            if output['DBInstance']['DBInstanceIdentifier'] == self.id:
                return True
        except Exception as e:
            logging.error('Instance ' + self.id + ' not deleted')
            logging.error(format(e))
        return False

    def waitDeleted(self):
        logging.notice('Waiting for deletion of ' + self.id + "...")
        waiter = self.aws.get_waiter('db_instance_deleted')
        try:
            waiter.wait(DBInstanceIdentifier=self.id)
            return True
        except:
            logging.error('Instance ' + self.id + ' not deleted')
            logging.error(format(e))
        return False

    def waitAvailable(self):
        logging.notice('Waiting ' + self.id + " to be available...")
        waiter = self.aws.get_waiter('db_instance_available')
        try:
            waiter.wait(DBInstanceIdentifier=self.id)
            return True
        except:
            logging.error('Instance ' + self.id + ' not available')
            logging.error(format(e))
        return False
