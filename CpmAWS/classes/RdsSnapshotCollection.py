import logging

from CpmAWS.core.Collection import Collection
from RdsSnapshot import RdsSnapshot


class RdsSnapshotCollection(Collection):
    snapshots      = {}
    snapshot_olds  = []
    instanceModule = 'RdsSnapshot'

    def list(self):
        # list all snapshots for our instances
        # @TODO marker for pagintation of results, but at the moment only 50 manual snapshots are allowed on AWS
        logging.notice('Listing snapshots...')
        try:
            result = self.aws.describe_db_snapshots(
                SnapshotType='manual',
                MaxRecords=100,
                IncludeShared=False,
                IncludePublic=False
            )
        except Exception as e:
            logging.error(format(e))
            return False
        # filter them
        for awsObject in result['DBSnapshots']:
            snapshot = None
            snapshot = RdsSnapshot(self.orchestrator, self.aws)
            snapshot.load(awsObject)
            # filter with tag_key/value
            if snapshot.belongsToFilter(snapshot.tags.get('DBInstanceIdentifier')):
                # keep only last snapshot
                if not snapshot.awsObject['DBInstanceIdentifier'] in self.snapshots:
                    self.snapshots[snapshot.awsObject['DBInstanceIdentifier']] = snapshot
                    logging.info(snapshot.awsObject['DBSnapshotIdentifier'])
                else:
                    if snapshot.awsObject['SnapshotCreateTime'] > self.snapshots[snapshot.awsObject['DBInstanceIdentifier']].awsObject[
                            'SnapshotCreateTime']:
                        self.snapshot_olds.append(self.snapshots[snapshot.awsObject['DBInstanceIdentifier']])
                        self.snapshots[snapshot.awsObject['DBInstanceIdentifier']] = snapshot
                        logging.info(snapshot.awsObject['DBSnapshotIdentifier'])
                    else:
                        self.snapshot_olds.append(snapshot)
                        logging.info(snapshot.awsObject['DBSnapshotIdentifier'] + " too old")
            else:
                logging.info("ignored " + snapshot.awsObject['DBSnapshotIdentifier'])
        for dbinstanceidentifier in self.snapshots:
            logging.info("Instance with snapshot: " + dbinstanceidentifier
                + " : " + self.snapshots[dbinstanceidentifier].awsObject['DBSnapshotIdentifier'])
        for dbinstanceidentifier in self.snapshot_olds:
            logging.info("Old snapshot: " + dbinstanceidentifier.awsObject['DBSnapshotIdentifier'])
        return self.snapshots
