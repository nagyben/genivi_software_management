# (c) 2015 - Jaguar Land Rover.
#
# Mozilla Public License 2.0
#
# Python-based life cycle manager PoC



#import gtk
#import dbus
#import dbus.service
#from dbus.mainloop.glib import DBusGMainLoop
import sys
import time
import common.swm as swm
import subprocess

import rpyc

#
# Lifecycle manager service
#

class LifecycleManager(object):
    def start_components(self,
                         transaction_id,
                         components):

        print "Lifecycle Manager: Got start_components()"
        print "  Operation Transaction ID: {}".format(transaction_id)
        print "  Components:               {}".format(", ".join(components))
        print "---"

        # Simulate starting components
        # TODO: find out how to start a component on the IMC.
        print "Starting :"
        for i in components:
            print "    Starting: {} (3 sec)".format(i)
            time.sleep(3.0)
        print
        print "Done"
        swm.send_operation_result(transaction_id,
                                  swm.SWM_RES_OK,
                                  "Started components {}".format(", ".join(components)))
        return None

    def stop_components(self,
                        transaction_id,
                        components):

        print "Lifecycle Manager: Got stop_components()"
        print "  Operation Transaction ID: {}".format(transaction_id)
        print "  Components:               {}".format(", ".join(components))
        print "---"

        # Simulate stopping components
        try:
            print "Stopping :"
            for i in components:
                #TODO: test whether this actually works on the IMC
                print "    Stopping: {} (3 sec)".format(i)
                subprocess.check_call("pkill -f {}".format(i), shell=True)
                time.sleep(3.0)
            print
            print "Done"
            swm.send_operation_result(transaction_id,
                                      swm.SWM_RES_OK,
                                      "Stopped components {}".format(", ".join(components)))

        except subprocess.CalledProcessError as e:
            print "stop_components() CalledProcessError returncode: {}".format(e.returncode)
            print str(e)
            swm.send_operation_result(transaction_id,
                                      swm.SWM_RES_INTERNAL_ERROR,
                                      "Internal_error: {}".format(e))

        except Exception as e:
            print "stop_components() Exception: {}".format(e)
            print str(e)
            swm.send_operation_result(transaction_id,
                                      swm.SWM_RES_INTERNAL_ERROR,
                                      "Internal_error: {}".format(e))

        return None

class LCMgrService(rpyc.Service):
    def on_connect(self):
        print "A client connected"

    def on_disconnect(self):
        print "A client disconnected"

    def exposed_start_components(self, transaction_id, components):
        """ function to expose start_components over RPyC
        """
        return LCMgr.start_components(transaction_id, components)

    def exposed_stop_components(self, transaction_id, components):
        """ function to expose stop_components over RPyC
        """
        return LCMgr.stop_components(transaction_id, components)


print
print "Lifecycle Manager."
print

print "Initializing LifecycleManager..."
LCMgr = LifecycleManager()

from rpyc.utils.server import ThreadedServer
t = ThreadedServer(LCMgrService, port = swm.PORT_LCMGR)
print "Starting LCMgrService ThreadServer on port " +  str(swm.PORT_LCMGR)
t.start()
