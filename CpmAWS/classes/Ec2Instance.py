import boto3
import logging

from CpmAWS.core.Aws import Aws
from CpmAWS.core.Tags import Tags


class Ec2Instance(Aws):
    arnService = 'ec2'
    arnType = 'instance'
    arnPropertyForId = 'InstanceId'

    # EC2 have a name that is not the id
    @property
    def name(self):
        return self.tags.get('Name')

    def AwsTagsGet(self):
        return self.aws.describe_tags(Filters=[{'Name': 'resource-id', 'Values': [self.id]}])['Tags']

    def stop(self):
        try:
            logging.notice('Stopping ' + self.name)
            ret = self.aws.stop_instances(InstanceIds=[self.id])
            for instance in ret['StoppingInstances']:
                if instance['InstanceId'] == self.id:
                    return True
        except Exception as e:
            logging.notice('Instance ' + self.name + ' not stopped')
            logging.error(format(e))

        return False

    def start(self):
        try:
            logging.notice('Starting ' + self.name)
            ret = self.aws.start_instances(InstanceIds=[self.id])
            for instance in ret['StartingInstances']:
                if instance['InstanceId'] == self.id:
                    return True
        except Exception as e:
            logging.notice('Instance ' + self.name + ' not started')
            logging.error(format(e))

        return False

    def waitstopped(self):
        try:
            logging.notice('Waiting for ' + self.name + ' to stop')
            waiter = self.aws.get_waiter('instance_stopped')
            waiter.wait(InstanceIds=[self.id])
            return True
        except Exception as e:
            logging.error('Wait for ' + self.name + ' failed')
            logging.error(format(e))
        return False

    def waitstarted(self):
        try:
            logging.notice('Waiting for ' + self.name + ' to be running')
            waiter = self.aws.get_waiter('instance_running')
            waiter.wait(InstanceIds=[self.id])
            return True
        except Exception as e:
            logging.error('Wait for Instance ' + self.name + ' failed')
            logging.error(format(e))
        return False
