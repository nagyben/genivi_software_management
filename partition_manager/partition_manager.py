# (c) 2015 - Jaguar Land Rover.
#
# Mozilla Public License 2.0
#
# Python-based partition manager PoC

import sys
import time
import common.swm as swm

import rpyc

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

        print "Partition Manager: create_disk_partition()"
        print "  Operfation Transaction ID: {}".format(transaction_id)
        print "  Disk:                      {}".format(disk)
        print "  Partition Number:          {}".format(partition_number)
        print "  Partition Type:            {}".format(partition_type)
        print "  Start:                     {}".format(start)
        print "  Size:                      {}".format(size)
        print "  GUID:                      {}".format(guid)
        print "  Name:                      {}".format(name)
        print "---"

        # Simulate install
        print "Simulating create partition: disk({}) partiton({}) (3 sec)".format(disk, partition_number)
        for i in xrange(1,30):
            sys.stdout.write('.')
            sys.stdout.flush()
            time.sleep(0.1)
        print
        print "Done"
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

        print "Partition Manager: resize_disk_partition()"
        print "  Operfation Transaction ID: {}".format(transaction_id)
        print "  Disk:                      {}".format(disk)
        print "  Partition Number:          {}".format(partition_number)
        print "  Start:                     {}".format(start)
        print "  Size:                      {}".format(size)
        print "---"

        # Simulate install
        print "Simulating resizing partition: disk({}) partiton({}) (10 sec)".format(disk, partition_number)
        for i in xrange(1,50):
            sys.stdout.write('.')
            sys.stdout.flush()
            time.sleep(0.2)
        print
        print "Done"
        swm.send_operation_result(transaction_id,
                                   swm.SWM_RES_OK,
                                   "Partition resize success. Disk: {}:{}".format(disk, partition_number))
        return None

    def delete_disk_partition(self,
                              transaction_id,
                              disk,
                              partition_number):

        print "Partition Manager: delete_disk_partition()"
        print "  Operfation Transaction ID: {}".format(transaction_id)
        print "  Disk:                      {}".format(disk)
        print "  Partition Number:          {}".format(partition_number)
        print "---"

        # Simulate install
        print "Simulating delete partition: disk({}) partiton({}) (5 sec)".format(disk, partition_number)
        for i in xrange(1,10):
            sys.stdout.write('.')
            sys.stdout.flush()
            time.sleep(0.2)
        print
        print "Done"
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

        print "Partition Manager: write_disk_partition()"
        print "  Operfation Transaction ID: {}".format(transaction_id)
        print "  Disk:                      {}".format(disk)
        print "  Partition Number:          {}".format(partition_number)
        print "  Image Path:                {}".format(image_path)
        #print "  Blacklisted Partitions:    {}".format(blacklisted_partitions)
        print "---"

        # Simulate write
        print "Simulating writing partition: disk({}) partiton({}) (10 sec)".format(disk, partition_number)
        for i in xrange(1,50):
            sys.stdout.write('.')
            sys.stdout.flush()
            time.sleep(0.2)
        print
        print "Done"
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

        print "Partition Manager: patch_disk_partition()"
        print "  Operfation Transaction ID: {}".format(transaction_id)
        print "  Disk:                      {}".format(disk)
        print "  Partition Number:          {}".format(partition_number)
        print "  Image Path:                {}".format(image_path)
        print "  Blacklisted Partitions:    {}".format(blacklisted_partitions)
        print "---"

        # Simulate patch
        print "Simulating patching partition: disk({}) partiton({}) (10 sec)".format(disk, partition_number)
        for i in xrange(1,50):
            sys.stdout.patch('.')
            sys.stdout.flush()
            time.sleep(0.2)
        print
        print "Done"
        swm.send_operation_result(transaction_id,
                                  swm.SWM_RES_OK,
                                  "Partition patch success. Disk: {}:{} Image: {}".
                                  format(disk, partition_number, image_path))
        return None



class PartMgrService(rpyc.Service):
    def on_connect(self):
        print "A client connected"

    def on_disconnect(self):
        print "A client disconnected"

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
print "Partition Manager."
print

print "Initializing PartitionManager..."
PartMgr = PartitionManager()

from rpyc.utils.server import ThreadedServer
t = ThreadedServer(PartMgrService, port = swm.PORT_PARTMGR)
print "Starting PartitionManager ThreadedServer on port " + str(swm.PORT_PARTMGR)
t.start()

#while True:
#    gtk.main_iteration()
