import logging

from CpmAWS.classes.RdsCollection import RdsCollection
from CpmAWS.classes.RdsSnapshot import RdsSnapshot
from CpmAWS.classes.RdsSnapshotCollection import RdsSnapshotCollection
from CpmAWS.core.Plugin import Plugin


class Rds(Plugin):
    def list(self):
        ok = True
        rdscollection = RdsCollection(self.orchestrator)
        if rdscollection.connect() == False:
            return False
        rdscollection.list()

        if len(rdscollection.instances) == 0:
            logging.error('No instance matching filter')
            return False
        else:
            for id,instance in rdscollection.instances.iteritems():
                print ' - Instance '+instance.name+\
                      ' status='+instance.get('DBInstanceStatus')
            return True

    def stop(self):
        ok = True
        rdscollection = RdsCollection(self.orchestrator)
        if rdscollection.connect() == False:
            return False
        rdscollection.list()

        if len(rdscollection.instances) == 0:
            logging.error('No instance matching filter')
            return False
        snapshotsok = {}
        # launch snapshots for all instances
        logging.notice('Creating snapshots...')
        for name, instance in rdscollection.instances.iteritems():
            # check instance state
            if instance.get('DBInstanceStatus') == 'available':
                instance.snapshot = RdsSnapshot(self.orchestrator, rdscollection.aws)
                if instance.snapshot.create(instance):
                    snapshotsok[name] = instance
            else:
                logging.error('Instance ' + name + 'status ' + instance.get('DBInstanceStatus'))
                ok = False
        if len(snapshotsok) == 0:
            logging.debug('No ok snapshot')
            return False

        waitok = []
        # wait for ok snapshots
        logging.notice('Waiting snapshots to complete...')
        for name, rdsinstance in snapshotsok.iteritems():
            logging.notice('Wait for ' + name)
            if rdsinstance.snapshot.wait():
                waitok.append(rdsinstance)
            else:
                ok = False
        if len(waitok) == 0:
            logging.debug('No snapshot')
            return False

        deleteok = []
        # delete instances with ok snapshots
        logging.notice('Deleting instances...')
        for instance in waitok:
            if instance.delete():
                deleteok.append(instance)
            else:
                logging.error('Failed to delete ' + instance.get('DBInstanceIdentifier'))
                ok = False

        # wait for deletion complete
        logging.notice('Waiting instances delete to complete...')
        for instance in deleteok:
            if not instance.waitDeleted():
                return False
        return ok

    def start(self):
        ok = True
        snapshotcollection = RdsSnapshotCollection(self.orchestrator)
        if snapshotcollection.connect() == False:
            logging.error('Listing snapshots error')
            return False
        if snapshotcollection.list() == False:
            return False

        snapshotsok = []
        # restore dbs
        logging.notice('Restoring snapshots...')
        for name, snapshot in snapshotcollection.snapshots.iteritems():
            if snapshot.restore():
                snapshotsok.append(snapshot)
            else:
                ok = False

        if len(snapshotsok) == 0:
            logging.debug('No snapshot restored')
            return False

        waitsnapshotok = []
        # wait for snapshot complete
        logging.notice('Waiting snapshots restore to complete...')
        for snapshot in snapshotsok:
            if snapshot.wait():
                waitsnapshotok.append(snapshot)
                ok = False
        if len(waitsnapshotok) == 0:
            logging.debug('No snapshot to wait')
            return False

        waitinstanceok = []
        # wait for db ready
        logging.notice('Waiting db available...')
        for snapshot in waitsnapshotok:
            if snapshot.rdsinstance.waitAvailable():
                waitinstanceok.append(snapshot)
                ok = False
        if len(waitinstanceok) == 0:
            logging.debug('No db ready')
            return False

        # delete snapshots
        logging.notice('Deleting snapshots...')
        for snapshot in waitinstanceok:
            if not snapshot.delete():
                ok = False

        return ok
