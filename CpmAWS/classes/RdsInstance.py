import logging

from CpmAWS.core.Aws import Aws


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
        properties = super(RdsInstance, self).getInstancePropertiesForSnapshot(awsObject)

        # if multiaz remove the availability zone
        if properties['MultiAZ'] is True:
            del (properties['AvailabilityZone'])

        logging.debug('Properties for snapshot ' + str(properties))
        return properties

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
