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
import swm

import rpyc

#
# ECU Module Loader service
#
class ECU1ModuleLoaderService(rpyc.Service):
    def __init__(self):
        #bus_name = dbus.service.BusName('org.genivi.module_loader_ecu1', bus=dbus.SessionBus())
        #dbus.service.Object.__init__(self, bus_name, '/org/genivi/module_loader_ecu1')
        pass

    #@dbus.service.method('org.genivi.module_loader_ecu1',
    #                     async_callbacks=('send_reply', 'send_error'))

    def exposed_flash_module_firmware(self, transaction_id, image_path, blacklisted_firmware, allow_downgrade, send_reply, send_error):
        """ function to expose flash_module_firmware over RPyC
        """
        return flash_module_firmware(self, transaction_id, image_path, blacklisted_firmware, allow_downgrade, send_reply, send_error)

    def flash_module_firmware(self,
                              transaction_id,
                              image_path,
                              blacklisted_firmware,
                              allow_downgrade,
                              send_reply,
                              send_error):


        print "Package Manager: Got flash_module_firmware()"
        print "  Operation Transaction ID: {}".format(transaction_id)
        print "  Image Path:               {}".format(image_path)
        print "  Blacklisted firmware:     {}".format(blacklisted_firmware)
        print "  Allow downgrade:          {}".format(allow_downgrade)
        print "---"

        # Send back an immediate reply since DBUS
        # doesn't like python dbus-invoked methods to do
        # their own calls (nested calls).
        #
        #FIXME: dbus reply
        send_reply(True)

        # Simulate install
        print "Intalling on ECU1: {} (5 sec):".format(image_path)
        for i in xrange(1,50):
            sys.stdout.write('.')
            sys.stdout.flush()
            time.sleep(0.1)
        print
        print "Done"
        swm.send_operation_result(transaction_id,
                                  swm.SWM_RES_OK,
                                  "Firmware flashing successful for ecu1. Path: {}".format(image_path))

        return None

    #@dbus.service.method('org.genivi.module_loader_ecu1')

    def exposed_get_module_firmware_version(self):
        """ function to expose get_module_firmware_version over RPyC
        """
        return get_module_firmware_version(self)

    def get_module_firmware_version(self):
        print "Got get_installed_packages()"
        return ("ecu1_firmware_1.2.3", 1452904544)

print
print "ECU1 Module Loader."
print

#DBusGMainLoop(set_as_default=True)
#module_loader_ecu1 = ECU1ModuleLoaderService()
from rpyc.utils.server import ThreadedServer
t = ThreadedServer(ECU1ModuleLoaderService, port = 90005)
t.start()

while True:
    #FIXME: gtk.main_interaction()
    gtk.main_iteration()
