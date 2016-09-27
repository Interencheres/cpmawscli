import logging
from fnmatch import fnmatch

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
        self.instances = self.filter(instances)
        for name in self.instances:
            logging.debug(name)
        return self.instances

    def instanceBelongsToFilter(self, instance):
        """As filters are not available for describe_db_instances, we need to
        implement it here
        @see https://docs.aws.amazon.com/cli/latest/reference/rds/describe-db-instances.html
        """
        for tag in self.parameters.tags:
            key = tag["Name"][4:]
            values = tag["Values"]
            if key == "Name":
                for name in values:
                    if not fnmatch(instance.name, name):
                        return False
            else:
                if instance.tags.get(key) not in values:
                    return False

        return super(RdsCollection, self).instanceBelongsToFilter(instance)
