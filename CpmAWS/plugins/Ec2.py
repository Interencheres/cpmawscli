import logging

from CpmAWS.classes.Ec2Collection import Ec2Collection
from CpmAWS.classes.Ec2Instance import Ec2Instance

from CpmAWS.core.Plugin import Plugin


class Ec2(Plugin):
    def list(self):
        """
            Lists the EC2 instances specified by the filters to stdout
        :return: success
        :rtype: bool
        """
        ec2collection = Ec2Collection(self.orchestrator)
        if ec2collection.connect() is False:
            return False

        if ec2collection.list() is False:
            return False
        for id, instance in ec2collection.instances.iteritems():
            print ' - Instance ' + instance.tags.get('Name') + ' status=' + instance.get('State')['Name']
        return True

    def stop(self):
        """
            Stops the running EC2 instances specified by the filters
        :return: success
        :rtype: bool
        """
        ec2collection = Ec2Collection(self.orchestrator)
        if ec2collection.connect() is False:
            logging.error('Impossible to connect')
            return False
        if ec2collection.list() is False:
            return False

        ok = True
        stoppinginstances = []
        logging.notice('Stopping instances...')
        for id, instance in ec2collection.instances.iteritems():
            if instance.awsObject['State']['Name'] == 'running':
                if instance.stop():
                    stoppinginstances.append(instance)
                else:
                    ok = False
            else:
                logging.warning('Skipping Instance ' + instance.name + ' is status ' + instance.awsObject['State']['Name'])

        logging.notice('Waiting instances to be stopped...')
        for instance in stoppinginstances:
            if not instance.waitstopped():
                ok = False
        return ok

    def start(self):
        """
            Starts the stopped EC2 instances specified by the filters
        :return: success
        :rtype: bool
        """
        ec2collection = Ec2Collection(self.orchestrator)
        if ec2collection.connect() is False:
            logging.error('Impossible to connect')
            return False
        if ec2collection.list() is False:
            return False

        ok = True
        startinginstances = []
        logging.notice('Starting instances...')
        for id, instance in ec2collection.instances.iteritems():
            if instance.awsObject['State']['Name'] == 'stopped':
                if instance.start():
                    startinginstances.append(instance)
                else:
                    ok = False
            else:
                logging.warning('Skipping Instance ' + instance.name + ' is status ' + instance.awsObject['State']['Name'])
                ok = False
        logging.notice('Waiting instances to be started...')
        for instance in startinginstances:
            if not instance.waitstarted():
                ok = False
        return ok
