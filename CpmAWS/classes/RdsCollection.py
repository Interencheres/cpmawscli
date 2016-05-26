import logging

from CpmAWS.core.Collection import Collection
from CpmAWS.classes.RdsInstance import RdsInstance


class RdsCollection(Collection):
    instances = {}
    instanceModule = 'RdsInstance'

    def list(self):
        instances = {}
        # list all instances
        try:
            logging.notice('Listing RDS instances...')
            arrayOfAwsObjects = self.aws.describe_db_instances()
            for awsObject in arrayOfAwsObjects['DBInstances']:
                instances[awsObject['DBInstanceIdentifier']] = RdsInstance(self.orchestrator, self.aws).load(awsObject)
                logging.debug(awsObject['DBInstanceIdentifier'])
        except Exception as e:
            logging.error(format(e))
            return False
        # filter them
        logging.notice('Filtering instances...')
        self.instances = self.filter(instances)
        for name in self.instances:
            logging.debug(name)
        return self.instances
