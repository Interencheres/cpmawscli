import boto3
import logging

from CpmAWS.classes.Ec2Instance import Ec2Instance
from CpmAWS.core.Collection import Collection


class Ec2Collection(Collection):
    instances = {}
    instanceModule = 'Ec2Instance'

    def list(self):
        instances = {}
        # list all instances
        try:
            logging.notice('Listing EC2 instances...')
            arrayOfAwsObjects = self.aws.describe_instances()
            for reservation in arrayOfAwsObjects['Reservations']:
                for awsObject in reservation['Instances']:
                    instances[instance.id]=Ec2Instance(self.orchestrator, self.aws).load(awsObject)
                    logging.debug(instance.tags.get('Name'))
        except Exception as e:
            logging.error(format(e))
            return False
        logging.notice('Filtering instances...')
        self.instances = self.filter(instances)
        for name in self.instances:
            logging.debug(name)
        return True



