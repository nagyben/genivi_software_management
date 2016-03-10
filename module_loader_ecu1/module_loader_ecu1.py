# (c) 2015 - Jaguar Land Rover.
#
# Mozilla Public License 2.0
#
# Python-based partition manager PoC



#import gtk
#import dbus
#import dbus.service
#from dbus.mainloop.glib import DBusGMainLoop
import sys
import time
import common.swm as swm

import rpyc

import logging

# configure logging
logFormatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger()

fileHandler = logging.FileHandler("logs/{}.log".format(__name__))
fileHandler.setFormatter(logFormatter)
logger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
logger.addHandler(consoleHandler)

#
# ECU Module Loader service
#

class ECU1ModuleLoader(object):
    def flash_module_firmware(self,
                              transaction_id,
                              image_path,
                              blacklisted_firmware,
                              allow_downgrade):


        logger.info("Package Manager: Got flash_module_firmware()")
        logger.info("  Operation Transaction ID: {}".format(transaction_id))
        logger.info("  Image Path:               {}".format(image_path))
        #logger.info("  Blacklisted firmware:     {}".format(blacklisted_firmware))
        logger.info("  Allow downgrade:          {}".format(allow_downgrade))
        logger.info("---")

        # Simulate install
        logger.info("Intalling on ECU1: {} (5 sec):".format(image_path))
        for i in xrange(1,50):
            sys.stdout.write('.')
            sys.stdout.flush()
            time.sleep(0.1)
        print
        logger.info("Done")
        swm.send_operation_result(transaction_id,
                                  swm.SWM_RES_OK,
                                  "Firmware flashing successful for ecu1. Path: {}".format(image_path))

        return None

    def get_module_firmware_version(self):
        logger.info("Got get_installed_packages()")
        return ("ecu1_firmware_1.2.3", 1452904544)



class ECU1ModuleLoaderService(rpyc.Service):
    def on_connect(self):
        logger.info("A client connected")

    def on_disconnect(self):
        logger.info("A client disconnected")

    def exposed_flash_module_firmware(self, transaction_id, image_path, blacklisted_firmware, allow_downgrade):
        """ function to expose flash_module_firmware over RPyC
        """
        return ecu1.flash_module_firmware(transaction_id, image_path, blacklisted_firmware, allow_downgrade)

    def exposed_get_module_firmware_version(self):
        """ function to expose get_module_firmware_version over RPyC
        """
        return ecu1.get_module_firmware_version()

print
logger.info("ECU1 Module Loader.")
print

logger.info("Initializing ECU1ModuleLoader...")
ecu1 = ECU1ModuleLoader()

from rpyc.utils.server import ThreadedServer
t = ThreadedServer(ECU1ModuleLoaderService, port = swm.PORT_ECU1)
logger.info("Starting ECU1 Module Loader ThreadedServer on port " + str(swm.PORT_ECU1))
t.start()
