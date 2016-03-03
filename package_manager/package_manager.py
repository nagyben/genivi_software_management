# (c) 2015 - Jaguar Land Rover.
#
# Mozilla Public License 2.0
#
# Python-based package manager PoC



#import gtk
#import dbus
#import dbus.service
#from dbus.mainloop.glib import DBusGMainLoop
import sys
import time
import swm

import rpyc

#
# Package manager service
#
class PkgMgrService(rpyc.Service):
    #def __init__(self):
    #    print "init package manager"
    #    #super(PkgMgrService, self).__init__(self._conn)
    #    #bus_name = dbus.service.BusName('org.genivi.package_manager', bus=dbus.SessionBus())
    #    #dbus.service.Object.__init__(self, bus_name, '/org/genivi/package_manager')
    #    pass

    #@dbus.service.method('org.genivi.package_manager',
    #                     async_callbacks=('send_reply', 'send_error'))

    def on_connect(self):
        print "A client connected"

    def on_disconnect(self):
        print "A client disconnected"

    def exposed_init_rpyc(self):
        pass

    def exposed_install_package(self, transaction_id, image_path, blacklisted_packages, send_reply, send_error):
        """ function to expose install_pacakge over rpyc
        """
        return self.install_package(transaction_id, image_path, blacklisted_packages, send_reply, send_error)

    def install_package(self,
                        transaction_id,
                        image_path,
                        blacklisted_packages,
                        send_reply,
                        send_error):

        try:
            print "Package Manager: Install Package"
            print "  Operation Transaction ID: {}".format(transaction_id)
            print "  Image Path:               {}".format(image_path)
            print "  Blacklisted packages:     {}".format(blacklisted_packages)
            print "---"

            #
            # Send back an immediate reply since DBUS
            # doesn't like python dbus-invoked methods to do
            # their own calls (nested calls).
            #
            #send_reply(True)

            # Simulate install
            print "Intalling package: {} (5 sec)".format(image_path)
            for i in xrange(1,50):
                sys.stdout.write('.')
                sys.stdout.flush()
                time.sleep(0.1)
            print
            print "Done"
            swm.send_operation_result(transaction_id,
                                      swm.SWM_RES_OK,
                                      "Installation successful. Path: {}".format(image_path))
        except Exception as e:
            print "install_package() Exception: {}".format(e)
            # traceback.print_exc()
            e.print_exc()
            swm.send_operation_result(transaction_id,
                                      swm.SWM_RES_INTERNAL_ERROR,
                                      "Internal_error: {}".format(e))
        return None


    #@dbus.service.method('org.genivi.package_manager',
    #                     async_callbacks=('send_reply', 'send_error'))

    def exposed_upgrade_pacakge(self, transaction_id, image_path, blacklisted_packages, allow_downgrade, send_reply, send_error):
        """ function to expose upgrade_package over rpyc
        """
        return self.upgrade_package(transaction_id, image_path, blacklisted_packages, allow_downgrade, send_reply, send_error)

    def upgrade_package(self,
                        transaction_id,
                        image_path,
                        blacklisted_packages,
                        allow_downgrade,
                        send_reply,
                        send_error):

        try:
            print "Package Manager: Upgrade package"
            print "  Operation Transaction ID: {}".format(transaction_id)
            print "  Image Path:               {}".format(image_path)
            print "  Allow downgrade:          {}".format(allow_downgrade)
            print "  Blacklisted packages:     {}".format(blacklisted_packages)
            print "---"

            #
            # Send back an immediate reply since DBUS
            # doesn't like python dbus-invoked methods to do
            # their own calls (nested calls).
            #
            #send_reply(True)

            # Simulate install
            print "Upgrading package: {} (5 sec)".format(image_path)
            for i in xrange(1,50):
                sys.stdout.write('.')
                sys.stdout.flush()
                time.sleep(0.1)
            print
            print "Done"
            swm.send_operation_result(transaction_id,
                                      swm.SWM_RES_OK,
                                      "Upgrade successful. Path: {}".format(image_path))

        except Exception as e:
            print "upgrade_package() Exception: {}".format(e)
            #traceback.print_exc()
            e.print_exc()
            swm.send_operation_result(transaction_id,
                                      swm.SWM_RES_INTERNAL_ERROR,
                                      "Internal_error: {}".format(e))
        return None

    #@dbus.service.method('org.genivi.package_manager',
    #                     async_callbacks=('send_reply', 'send_error'))

    def exposed_remove_package(self, transaction_id, package_id, send_reply, send_error):
        """ function to expose remove_package over rpyc
        """
        return self.remove_package(transaction_id, package_id, send_reply, send_error)

    def remove_package(self,
                       transaction_id,
                       package_id,
                       send_reply,
                       send_error):
        try:
            print "Package Manager: Remove package"
            print "  Operation Transaction ID: {}".format(transaction_id)
            print "  Package ID:               {}".format(package_id)
            print "---"

            #
            # Send back an immediate reply since DBUS
            # doesn't like python dbus-invoked methods to do
            # their own calls (nested calls).
            #
            #send_reply(True)

            # Simulate remove
            print "Upgrading package: {} (5 sec)".format(package_id)
            for i in xrange(1,50):
                sys.stdout.write('.')
                sys.stdout.flush()
                time.sleep(0.1)
            print
            print "Done"
            swm.send_operation_result(transaction_id,
                                      swm.SWM_RES_OK,
                                      "Removal successful. Package_id: {}".format(package_id))
        except Exception as e:
            print "upgrade_package() Exception: {}".format(e)
            #traceback.print_exc()
            e.print_exc()
            swm.send_operation_result(transaction_id,
                                      swm.SWM_RES_INTERNAL_ERROR,
                                      "Internal_error: {}".format(e))
        return None
        return None

    #@dbus.service.method('org.genivi.package_manager')

    def exposed_get_installed_packages(self):
        """ function to expose get_installed_packages over rpyc
        """
        return self.get_installed_packages()

    def get_installed_packages(self):
        print "Got get_installed_packages()"
        return [ 'bluez_driver_1.2.2', 'bluez_apps_2.4.4' ]



print
print "Package Manager."
print


#DBusGMainLoop(set_as_default=True)
#pkg_mgr = PkgMgrService()
from rpyc.utils.server import ThreadedServer
t = ThreadedServer(PkgMgrService, port = swm.PORT_PACKMGR)

print "Starting Package Manager rpyc service on port " + str(swm.PORT_PACKMGR)
t.start()

#while True:
#    gtk.main_iteration()
