import logging
from datetime import datetime

from CpmAWS.classes.RdsInstance import RdsInstance
from CpmAWS.core.Aws import Aws


class RdsSnapshot(Aws):
    awsObject = {}
    arnService = 'rds'
    arnType = 'snapshot'
    arnPropertyForId = 'DBSnapshotIdentifier'
    dbsnapshotidentifier = None
    rdsinstance = None

    def create(self, rdsObject):
        self.dbsnapshotidentifier = self.configuration.get('dbSnapshotPrefix') + "-" + rdsObject.awsObject[
            'DBInstanceIdentifier'] + "-" + datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        logging.notice('Creating snapshot ' + self.dbsnapshotidentifier + "...")
        tags = rdsObject.makeTagsForSnapshot()
        # for ease add plain tags
        for key, value in self.getTagFilter().iteritems():
            tags.append({'Key': key, 'Value': value})
        tags.append({'Key': 'DBInstanceIdentifier', 'Value': rdsObject.awsObject['DBInstanceIdentifier']})

        if not self.parameters.dryrun:
            try:
                self.awsObject = self.aws.create_db_snapshot(
                    DBSnapshotIdentifier=self.dbsnapshotidentifier,
                    DBInstanceIdentifier=rdsObject.awsObject['DBInstanceIdentifier'],
                    Tags=tags
                )
                return isinstance(self.awsObject['DBSnapshot']['DBSnapshotIdentifier'], str)
            except Exception as e:
                logging.error(format(e))
        else:
            logging.warning('Dryrun, not creating snapshot')
        return False

    def wait(self):
        logging.notice("waiting for " + self.dbsnapshotidentifier + " to complete...")
        if not self.parameters.dryrun:
            try:
                ret = self.aws.get_waiter('db_snapshot_completed').wait(
                    DBSnapshotIdentifier=self.dbsnapshotidentifier,
                    SnapshotType='manual',
                )
                if ret is None:
                    return True
            except Exception as e:
                logging.error('Wait failed for ' + self.dbsnapshotidentifier)
                logging.error(format(e))
                return False
        else:
            logging.warning('Dryrun not waiting')
            return True
        return False

    def restore(self):
        # test if instance already exist
        if RdsInstance(self.orchestrator, self.aws).exist(self.awsObject['DBInstanceIdentifier']):
            logging.error(' Not restoring existing ' + self.awsObject['DBInstanceIdentifier'])
            return False
        # restore instance
        params = self.decodeTags(RdsInstance(self.orchestrator, self.aws))
        if not self.parameters.dryrun:
            try:
                params['DBSnapshotIdentifier'] = self.get('DBSnapshotIdentifier')
                self.dbsnapshotidentifier = self.get('DBSnapshotIdentifier')
                ret = self.aws.restore_db_instance_from_db_snapshot(**params)
                if ret['DBInstance']['DBInstanceIdentifier'] == self.awsObject['DBInstanceIdentifier']:
                    self.rdsinstance = RdsInstance(self.orchestrator, self.aws)
                    self.rdsinstance.load(ret['DBInstance'])
                    return True
            except Exception as e:
                logging.error('snapshot ' + self.get('DBSnapshotIdentifier') + ' not restored')
                logging.error(format(e))
        else:
            logging.warning('Dryrun not restoring')
            return True
        return False

    def delete(self):
        logging.notice('Deleting snapshot ' + self.get('DBSnapshotIdentifier'))
        try:
            self.aws.delete_db_snapshot(
                DBSnapshotIdentifier=self.get('DBSnapshotIdentifier')
            )
            return True
        except Exception as e:
            logging.error('snapshot ' + self.get('DBSnapshotIdentifier') + ' not deleted')
            logging.error(format(e))
            return False
            # does object comply with command line filtering parameters

    def belongsToFilter(self, instanceIdentifier):
        for tag in self.parameters.tags:
            key = tag["Name"][4:]
            values = tag["Values"]
            if self.tags.get(key) not in values:
                return False

        if self.parameters.instance and (instanceIdentifier != self.parameters.instance):
            return False
        return True

    def getTagFilter(self):
        tags = {}
        for tag in self.parameters.tag:
            tags[tag["Name"][4:]] = tag["Values"][0]
        return tags

    def AwsTagsGet(self):
        return self.aws.list_tags_for_resource(ResourceName=self.getArn())['TagList']
