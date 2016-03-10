# (c) 2015 - Jaguar Land Rover.
#
# Mozilla Public License 2.0
#
# Python-based life cycle manager PoC


import time
import common.swm as swm
import subprocess

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
# Lifecycle manager service
#

class LifecycleManager(object):
    def start_components(self,
                         transaction_id,
                         components):

        logger.info("Lifecycle Manager: Got start_components()")
        logger.info("  Operation Transaction ID: {}".format(transaction_id))
        logger.info("  Components:               {}".format(", ".join(components)))
        logger.info("---")

        # Simulate starting components
        # TODO: find out how to start a component on the IMC.
        logger.info("Starting :")
        for i in components:
            logger.info("    Starting: {} (3 sec)".format(i))
            time.sleep(3.0)
        print
        logger.info("Done")
        swm.send_operation_result(transaction_id,
                                  swm.SWM_RES_OK,
                                  "Started components {}".format(", ".join(components)))
        return None

    def stop_components(self,
                        transaction_id,
                        components):

        logger.info("Lifecycle Manager: Got stop_components()")
        logger.info("  Operation Transaction ID: {}".format(transaction_id))
        logger.info("  Components:               {}".format(", ".join(components)))
        logger.info("---")

        # Simulate stopping components
        try:
            logger.info("Stopping :")
            for i in components:
                #TODO: test whether this actually works on the IMC
                logger.info("    Stopping: {} (3 sec)".format(i))
                subprocess.check_call("pkill -f {}".format(i), shell=True)
                time.sleep(3.0)
            print
            logger.info("Done")
            swm.send_operation_result(transaction_id,
                                      swm.SWM_RES_OK,
                                      "Stopped components {}".format(", ".join(components)))

        except subprocess.CalledProcessError as e:
            logger.exception("stop_components() CalledProcessError returncode: {}".format(e.returncode))
            logger.exception(str(e))
            swm.send_operation_result(transaction_id,
                                      swm.SWM_RES_INTERNAL_ERROR,
                                      "Internal_error: {}".format(e))

        except Exception as e:
            logger.exception("stop_components() Exception: {}".format(e))
            logger.exception(str(e))
            swm.send_operation_result(transaction_id,
                                      swm.SWM_RES_INTERNAL_ERROR,
                                      "Internal_error: {}".format(e))

        return None

class LCMgrService(rpyc.Service):
    def on_connect(self):
        logger.info("A client connected")

    def on_disconnect(self):
        logger.info("A client disconnected")

    def exposed_start_components(self, transaction_id, components):
        """ function to expose start_components over RPyC
        """
        return LCMgr.start_components(transaction_id, components)

    def exposed_stop_components(self, transaction_id, components):
        """ function to expose stop_components over RPyC
        """
        return LCMgr.stop_components(transaction_id, components)


print
logger.info("Lifecycle Manager.")
print

logger.info("Initializing LifecycleManager...")
LCMgr = LifecycleManager()

from rpyc.utils.server import ThreadedServer
t = ThreadedServer(LCMgrService, port = swm.PORT_LCMGR)
logger.info("Starting LCMgrService ThreadServer on port " +  str(swm.PORT_LCMGR))
t.start()
