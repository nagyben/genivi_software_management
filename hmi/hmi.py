# (c) 2015 - Jaguar Land Rover.
#
# Mozilla Public License 2.0
#
# Python-based hmi PoC for Software Loading Manager
#

import time
import threading
import traceback
import common.swm as swm

import logging
import rpyc

# configure logging
logFormatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

fileHandler = logging.FileHandler("logs/{}.log".format(__name__))
fileHandler.setFormatter(logFormatter)
logger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
logger.addHandler(consoleHandler)

class DisplayProgress(threading.Thread):

    def __init__(self, *arg):
        super(DisplayProgress, self).__init__(*arg)
        self.in_progress = True
        self.update_description = None
        self.update_start_time = None
        self.update_stop_time = None
        self.operation_hmi_message = None
        self.operation_start_time = None
        self.operation_stop_time = None

    def set_manifest(self, description, start_time, stop_time):
        self.update_description = description
        self.update_start_time = start_time
        self.update_stop_time = stop_time


    def set_operation(self, hmi_message, start_time, stop_time):
        self.operation_hmi_message = hmi_message
        self.operation_start_time = start_time
        self.operation_stop_time = stop_time


    def exit_thread(self):
        self.in_progress = False
        self.join()

    def run(self):
        while self.in_progress:
            if not self.update_description:
                time.sleep(0.5)
                continue

            time.sleep(0.1)


            ct = time.time()
            if self.update_stop_time >= ct:
                completion = (self.update_stop_time - ct) / (self.update_stop_time - self.update_start_time)
            else:
                completion = 0.0

            print "\033[HUpdate:    {}\033[K".format(self.update_description)

            print "{}{}\033[K".format("+"*int(60.0 - completion*60), "-"*int(completion*60))


            # If no operation is in progress, clear sreen
            if not self.operation_start_time:
                continue

            if self.update_stop_time >= ct:
                completion = (self.operation_stop_time - ct) / (self.operation_stop_time - self.operation_start_time)
            else:
                completion = 0.0

            print "\nOperation: {}\033[K".format(self.operation_hmi_message)
            print "{}{}".format("+"*int(60.0 - completion*60), "-"*int(completion*60))
            print "\033[J"

#
# Human Machine Interface Service
#

class HMI(object):
    def __init__(self):
        self.progress_thread = DisplayProgress()
        self.progress_thread.start()

    def update_notification(self,
                            update_id,
                            description):

        try:
            logger.info("HMI:  update_notification()")
            logger.info("  ID:            {}".format(update_id))
            logger.info("  description:   {}".format(description))
            logger.info("---")

            print
            print
            logger.info("DIALOG:")
            logger.info("DIALOG: UPDATE AVAILABLE")
            logger.info("DIALOG:   update_id:   {}".format(update_id))
            logger.info("DIALOG:   Description: {}".format(description))
            logger.info("DIALOG:")
            logger.info("DIALOG: Process? (yes/no)")

            # If we use input or raw_input, the whole dbus loop hangs after
            # this method returns, for some reason.
            #tcflush(sys.stdin, TCIOFLUSH)
            #resp = sys.stdin.read(1)
            #tcflush(sys.stdin, TCIOFLUSH)

            resp = raw_input("DIALOG: Process? (yes/no): ")
            print

            if len(resp) == 0 or (resp[0] != 'y' and resp[0] != 'Y'):
                approved = False
            else:
                approved = True

            #
            # Call software_loading_manager.package_confirmation()
            # to inform it of user approval / decline.
            #
            swlm_rpyc = rpyc.connect("localhost", swm.PORT_SWLM)
            swlm_rpyc.root.update_confirmation(update_id, approved)

        except Exception as e:
            logger.exception("Exception: {}".format(e))
            traceback.print_exc()

        return None

    def manifest_started(self,
                         update_id,
                         total_time_estimate,
                         description):
        try:
            logger.info("Manifest started")
            #send_reply(True)
            print "\033[H\033[J"
            ct = time.time()
            self.progress_thread.set_manifest(description,
                                              ct,
                                              ct + float(total_time_estimate) / 1000.0)

        except Exception as e:
            logger.exception("Exception: {}".format(e))
            traceback.print_exc()

        return None

    def operation_started(self,
                          operation_id,
                          time_estimate,
                          description):

        try:
            logger.info("Op started")
            #send_reply(True)
            ct = time.time()
            self.progress_thread.set_operation(description, ct, ct + float(time_estimate) / 1000.0)
        except Exception as e:
            logger.exception("Exception: {}".format(e))
            traceback.print_exc()
        return None

    def update_report(self,
                      update_id,
                      results):
        try:
            #send_reply(True)
            self.progress_thread.exit_thread()
            logger.info("Update report")
            logger.info("  ID:          {}".format(update_id))
            logger.info("  results:")
            for result in results:
                logger.info("    operation_id: {}".format(result['id']))
                logger.info("    code:         {}".format(result['result_code']))
                logger.info("    text:         {}".format(result['result_text']))
                logger.info("  ---")
            logger.info("---")
        except Exception as e:
            logger.exception("Exception: {}".format(e))
            traceback.print_exc()
        return None


class HMIService(rpyc.Service):
    def on_connect(self):
        logger.info("A client connected")

    def on_disconnect(self):
        logger.info("A client disconnected")

    def exposed_update_notification(self, update_id, description):
        """ function to expose update_notification over rpyc
        """
        return hmi.update_notification(update_id, description)

    def exposed_manifest_started(self, update_id, total_time_estimate, description):
        """ function to expose manifest_started over rpyc
        """
        return hmi.manifest_started(update_id, total_time_estimate, description)

    def exposed_operation_started(self, operation_id, time_estimate, description):
        """ function to expose operation_started over rpyc
        """
        return hmi.operation_started(operation_id, time_estimate, description)

    def exposed_update_report(self, update_id, results):
        """ function to expose update_report over rpyc
        """
        return hmi.update_report(update_id, results)

print
logger.info("HMI Simulator")
logger.info("Please enter package installation approval when prompted")
print

#gtk.gdk.threads_init() TODO: will this break the threads?

logger.info("Initializing HMI...")
hmi = HMI()

from rpyc.utils.server import ThreadedServer
t = ThreadedServer(HMIService, port = swm.PORT_HMI)
logger.info("Starting HMIService ThreadServer on port " + str(swm.PORT_HMI))
t.start()
