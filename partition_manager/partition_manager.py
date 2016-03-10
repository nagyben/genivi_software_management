# (c) 2015 - Jaguar Land Rover.
#
# Mozilla Public License 2.0
#
# Python-based partition manager PoC

import sys
import time
import common.swm as swm

import rpyc

import logging

# configure logging
logFormatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

fileHandler = logging.FileHandler("logs/{}.log".format(__name__))
fileHandler.setFormatter(logFormatter)
logger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
logger.addHandler(consoleHandler)

#
# Partition manager service
#

class PartitionManager(object):
    def create_disk_partition(self,
                              transaction_id,
                              disk,
                              partition_number,
                              partition_type,
                              start,
                              size,
                              guid,
                              name):

        logger.info("Partition Manager: create_disk_partition()")
        logger.info("  Operfation Transaction ID: {}".format(transaction_id))
        logger.info("  Disk:                      {}".format(disk))
        logger.info("  Partition Number:          {}".format(partition_number))
        logger.info("  Partition Type:            {}".format(partition_type))
        logger.info("  Start:                     {}".format(start))
        logger.info("  Size:                      {}".format(size))
        logger.info("  GUID:                      {}".format(guid))
        logger.info("  Name:                      {}".format(name))
        logger.info("---")

        # Simulate install
        logger.info("Simulating create partition: disk({}) partiton({}) (3 sec)".format(disk, partition_number))
        for i in xrange(1,30):
            sys.stdout.write('.')
            sys.stdout.flush()
            time.sleep(0.1)
        print
        logger.info("Done")
        swm.send_operation_result(transaction_id,
                                  swm.SWM_RES_OK,
                                  "Partition create successful. Disk: {}:{}".format(disk, partition_number))

        return None

    def resize_disk_partition(self,
                              transaction_id,
                              disk,
                              partition_number,
                              start,
                              size):

        logger.info("Partition Manager: resize_disk_partition()")
        logger.info("  Operfation Transaction ID: {}".format(transaction_id))
        logger.info("  Disk:                      {}".format(disk))
        logger.info("  Partition Number:          {}".format(partition_number))
        logger.info("  Start:                     {}".format(start))
        logger.info("  Size:                      {}".format(size))
        logger.info("---")

        # Simulate install
        logger.info("Simulating resizing partition: disk({}) partiton({}) (10 sec)".format(disk, partition_number))
        for i in xrange(1,50):
            sys.stdout.write('.')
            sys.stdout.flush()
            time.sleep(0.2)
        print
        logger.info("Done")
        swm.send_operation_result(transaction_id,
                                   swm.SWM_RES_OK,
                                   "Partition resize success. Disk: {}:{}".format(disk, partition_number))
        return None

    def delete_disk_partition(self,
                              transaction_id,
                              disk,
                              partition_number):

        logger.info("Partition Manager: delete_disk_partition()")
        logger.info("  Operfation Transaction ID: {}".format(transaction_id))
        logger.info("  Disk:                      {}".format(disk))
        logger.info("  Partition Number:          {}".format(partition_number))
        logger.info("---")

        # Simulate install
        logger.info("Simulating delete partition: disk({}) partiton({}) (5 sec)".format(disk, partition_number))
        for i in xrange(1,10):
            sys.stdout.write('.')
            sys.stdout.flush()
            time.sleep(0.2)
        print
        logger.info("Done")
        swm.send_operation_result(transaction_id,
                                   swm.SWM_RES_OK,
                                   "Partition delete success. Disk: {}:{}".format(disk, partition_number))

        return None

    def write_disk_partition(self,
                             transaction_id,
                             disk,
                             partition_number,
                             image_path,
                             blacklisted_partitions):

        logger.info("Partition Manager: write_disk_partition()")
        logger.info("  Operfation Transaction ID: {}".format(transaction_id))
        logger.info("  Disk:                      {}".format(disk))
        logger.info("  Partition Number:          {}".format(partition_number))
        logger.info("  Image Path:                {}".format(image_path))
        #logger.info("  Blacklisted Partitions:    {}".format(blacklisted_partitions))
        logger.info("---")

        # Simulate write
        logger.info("Simulating writing partition: disk({}) partiton({}) (10 sec)".format(disk, partition_number))
        for i in xrange(1,50):
            sys.stdout.write('.')
            sys.stdout.flush()
            time.sleep(0.2)
        print
        logger.info("Done")
        swm.send_operation_result(transaction_id,
                                  swm.SWM_RES_OK,
                                  "Partition write success. Disk: {}:{} Image: {}".
                                  format(disk, partition_number, image_path))

        return None

    def patch_disk_partition(self,
                             transaction_id,
                             disk,
                             partition_number,
                             image_path,
                             blacklisted_partitions):

        logger.info("Partition Manager: patch_disk_partition()")
        logger.info("  Operfation Transaction ID: {}".format(transaction_id))
        logger.info("  Disk:                      {}".format(disk))
        logger.info("  Partition Number:          {}".format(partition_number))
        logger.info("  Image Path:                {}".format(image_path))
        logger.info("  Blacklisted Partitions:    {}".format(blacklisted_partitions))
        logger.info("---")

        # Simulate patch
        logger.info("Simulating patching partition: disk({}) partiton({}) (10 sec)".format(disk, partition_number))
        for i in xrange(1,50):
            sys.stdout.patch('.')
            sys.stdout.flush()
            time.sleep(0.2)
        print
        logger.info("Done")
        swm.send_operation_result(transaction_id,
                                  swm.SWM_RES_OK,
                                  "Partition patch success. Disk: {}:{} Image: {}".
                                  format(disk, partition_number, image_path))
        return None



class PartMgrService(rpyc.Service):
    def on_connect(self):
        logger.info("A client connected")

    def on_disconnect(self):
        logger.info("A client disconnected")

    def exposed_create_disk_partition(self, transaction_id, disk, partition_number, partition_type, start, size, guid, name):
        """ function to expose create_disk_partition over RPyC
        """
        return PartMgr.create_disk_partition(transaction_id, disk, partition_number, partition_type, start, size, guid, name)

    def exposed_resize_disk_partition(self, transaction_id, disk, partition_number, start, size):
        """ function to expose resize_disk_partition over RPyC
        """
        return PartMgr.resize_disk_partition(transaction_id, disk, partition_number, start, size)

    def exposed_delete_disk_partition(self, transaction_id, disk, partition_number):
        """ function to expose delete_disk_partition over rpyc
        """
        return PartMgr.delete_disk_partition(transaction_id, disk, partition_number)

    def exposed_write_disk_partition(self, transaction_id, disk, partition_number, image_path, blacklisted_partitions):
        """ function to expose write_disk_partition over rpyc
        """
        return PartMgr.write_disk_partition(transaction_id, disk, partition_number, image_path, blacklisted_partitions)

    def exposed_patch_disk_partition(self, transaction_id, disk, partition_number, image_path, blacklisted_partitions):
        """ function to expose patch_disk_partition over rpyc
        """
        return PartMgr.patch_disk_partition(transaction_id, disk, partition_number, image_path, blacklisted_partitions)

print
logger.info("Partition Manager.")
print

logger.info("Initializing PartitionManager...")
PartMgr = PartitionManager()

from rpyc.utils.server import ThreadedServer
t = ThreadedServer(PartMgrService, port = swm.PORT_PARTMGR)
logger.info("Starting PartitionManager ThreadedServer on port " + str(swm.PORT_PARTMGR))
t.start()

#while True:
#    gtk.main_iteration()
