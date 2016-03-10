# (c) 2015 - Jaguar Land Rover.
#
# Mozilla Public License 2.0
#
# Python dbus service that coordinates all use cases.
#
#import gtk
#import dbus.service
#from dbus.mainloop.glib import DBusGMainLoop
import manifest_processor
import traceback
import sys
import getopt
import os
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
# Define the DBUS-facing Software Loading Manager service
#

class SoftwareLoadingManager(object):
    def __init__(self, db_path):
        self.manifest_processor = manifest_processor.ManifestProcessor(db_path)

    def initiate_download(self, package_id):
        sc_rpyc = rpyc.connect("localhost", swm.PORT_SC)
        sc_rpyc.root.initiate_download(package_id)

    #
    # Distribute a report of a completed installation
    # to all involved parties. So far those parties are
    # the HMI and the SOTA client
    #
    def distribute_update_result(self,
                                 update_id,
                                 results):
        # Send installation report to HMI
        logger.info("Sending report to hmi.update_report()")
        hmi_rpyc = rpyc.connect("localhost", swm.PORT_HMI)
        hmi_rpyc.root.update_report(update_id, results)

        # Send installation report to SOTA
        logger.info("Sending report to sota.update_report()")
        sc_rpyc = rpyc.connect("localhost", swm.PORT_SC)
        sc_rpyc.root.update_report(update_id, results)

    def get_current_manifest(self):
        return self.manifest_processor.current_manifest

    def start_next_manifest(self):
        if not self.manifest_processor.load_next_manifest():
            return False

        manifest = self.get_current_manifest()
        self.inform_hmi_of_new_manifest(manifest)
        #
        # This whole manifest may already have been executed and stored
        # as completed by the manifest_processor. If so, distribute the
        # given result
        #
        if not manifest.start_next_operation():
            self.distribute_update_result(manifest.update_id,
                                          manifest.operation_results)
            # Recursively call self to engage next manifest.
            return self.start_next_manifest()

        self.inform_hmi_of_new_operation(manifest.active_operation)
        return True

    def inform_hmi_of_new_operation(self,op):
        hmi_rpyc = rpyc.connect("localhost", swm.PORT_HMI)
        hmi_rpyc.root.operation_started(op.operation_id, op.time_estimate, op.description)
        return None

    def inform_hmi_of_new_manifest(self,manifest):
        total_time = 0
        for op in manifest.operations:
            total_time = total_time + op.time_estimate

        hmi_rpyc = rpyc.connect("localhost", swm.PORT_HMI)
        hmi_rpyc.root.manifest_started(manifest.update_id, total_time, manifest.description)
        return None

    def start_next_operation(self):
        #
        # If we are currently not processing an image, load
        # the one we just queued.
        #

        #
        # No manifest loaded.
        # Load next manifest and, if successful, start the
        # fist operation in said manifest
        #
        manifest = self.get_current_manifest()
        if not manifest:
            return self.start_next_manifest()

        # We have an active manifest. Check if we have an active operation.
        # If so return success
        if  manifest.active_operation:
            return True

        # We have an active manifest, but no active operation.
        # Try to start the next operation.
        # If that fails, we are out of operations in the current
        # manifest. Try to load the next manifest, which
        # will also start its first operation.
        if not manifest.start_next_operation():
            return self.manifest_processor.load_next_manifest()

        # Inform HMI of active operation
        self.inform_hmi_of_new_operation(manifest.active_operation)
        return True

    def update_available(self,
                         update_id,
                         description,
                         signature,
                         request_confirmation):

        logger.info("Got download available")
        logger.info("  ID:      {}".format(update_id))
        logger.info("  descr:   {}".format(description))
        logger.info("  confirm: {}".format(request_confirmation))

        #
        # Send a notification to the HMI to get user approval / decline
        # Once user has responded, HMI will invoke self.package_confirmation()
        # to drive the use case forward.
        #
        if request_confirmation:
            hmi_rpyc = rpyc.connect("localhost", swm.PORT_HMI)
            hmi_rpyc.root.update_notification(update_id, description)

            logger.info("  Called hmi.update_notification()")
            logger.info("---")
            return None

        logger.info("  No user confirmation requested. Will initiate download")
        logger.info("---")
        self.initiate_download(update_id)
        return None

    def update_confirmation(self,
                            update_id,
                            approved):

        logger.info("Got update_confirmation().")
        logger.info("  Approved: {}".format(approved))
        logger.info("  ID:       {}".format(update_id))
        if approved:
            #
            # Call the SOTA client and ask it to start the download.
            # Once the download is complete, SOTA client will call
            # download complete on this process to actually
            # process the package.
            #
            logger.info("Approved: Will call initiate_download()")
            self.initiate_download(update_id)
            logger.info("Approved: Called sota_client.initiate_download()")
            logger.info("---")
        else:
            # User did not approve. Send installation report
            logger.info("Declined: Will call installation_report()")
            self.distribute_update_result(update_id, [
                swm.result('N/A',
                           swm.SWM_RES_USER_DECLINED,
                           "Installation declined by user")
            ])

            logger.info("Declined. Called sota_client.installation_report()")
            logger.info("---")

        return None

    def download_complete(self,
                          update_image,
                          signature):

        logger.info("Got download complete")
        logger.info("  path:      {}".format(update_image))
        logger.info("  signature: {}".format(signature))
        logger.info("---")

        #
        # Send back an immediate reply since DBUS
        # doesn't like python dbus-invoked methods to do
        # their own calls (nested calls).
        #
        #send_reply(True)
        logger.warning("FIXME: Check signature of update image")

        #
        # Queue the image.
        #
        try:
            self.manifest_processor.queue_image(update_image)
            self.start_next_operation()
        except Exception as e:
            logger.exception("Failed to process downloaded update: {}".format(e))
            traceback.print_exc()

        return None

    #
    # Receive and process a installation report.
    # Called by package_manager, partition_manager, or ecu_module_loader
    # once they have completed their process_update() calls invoked
    # by software_loading_manager
    #
    def operation_result(self,
                         transaction_id,
                         result_code,
                         result_text):

        try:
            logger.info("Got operation_result()")
            logger.info("  transaction_id: {}".format(transaction_id))
            logger.info("  result_code:    {}".format(result_code))
            logger.info("  result_text:    {}".format(result_text))
            logger.info("---")

            manifest = self.get_current_manifest()
            if not manifest:
                logger.info("Warning: No manifest to handle callback reply")
                return None

            manifest.complete_transaction(transaction_id, result_code, result_text)
            if not self.start_next_operation():
                self.distribute_update_result(manifest.update_id,
                                              manifest.operation_results)
        except Exception as e:
            logger.info("Failed to process operation result: {}".format(e))
            traceback.print_exc()

    def get_installed_packages(self, include_packegs, include_module_firmware):
        logger.info("Got get_installed_packages()")
        return [ "bluez_driver", "bluez_apps" ]


class SLMService(rpyc.Service):
    def on_connect(self):
        logger.info("A client connected")

    def on_disconnect(self):
        logger.info("A client disconnected")

    def exposed_initiate_download(self, package_id):
        """ function to expose update_report to RPyC
        """
        return SLM.initiate_download(package_id)

    def exposed_update_available(self, update_id, description, signature, request_confirmation):
        """ function to expose update_available over RPyC
        """
        return SLM.update_available(update_id, description, signature, request_confirmation)

    def exposed_update_confirmation(self, update_id, approved):
        """ function to expose update_confirmation over RPyC
        """
        return SLM.update_confirmation( update_id, approved)

    def exposed_download_complete(self, update_image, signature):
        """ function to expose download_complete over RPyC
        """
        return SLM.download_complete(update_image, signature)

    def exposed_operation_result(self, transaction_id, result_code, result_text):
        """ function to expose operation_result over RPyC
        """
        return SLM.operation_result(transaction_id, result_code, result_text)

    def exposed_get_installed_packages(self, include_packegs, include_module_firmware):
        """ function to expose get_installed_packages over RPyC
        """
        return SLM.get_installed_packages(include_packegs, include_module_firmware)


def usage():
    print "Usage:", sys.argv[0], "[-r] [-d database_file] "
    print
    print "  -r                Reset the completed operations database prior to running"
    print "  -d database_file  Path to database file to store completed operations in"
    print
    print "Example:", sys.argv[0],"-r -d /tmp/database"
    sys.exit(255)

# === Entry point ===

print
logger.info("Software Loading Manager.")
print

try:
    opts, args= getopt.getopt(sys.argv[1:], "rd:")

except getopt.GetoptError as e:
    logger.exception("Could not parse arguments.")
    usage()

db_path = "/tmp/completed_operations.json"
reset_db = False

for o, a in opts:
    if o == "-r":
        reset_db = True
    elif o == "-d":
        db_path = a
    else:
        logger.warning("Unknown option: {}".format(o))
        usage()

#DBusGMainLoop(set_as_default=True)

# Check if we are to delete the old database.
if reset_db:
    try:
        os.remove(db_path)
    except:
        pass

# register service over RPyC

logger.info("Initializing SoftwareLoadingManager...")
SLM = SoftwareLoadingManager(db_path)

from rpyc.utils.server import ThreadedServer
t = ThreadedServer(SLMService, port = swm.PORT_SWLM)
logger.info("Starting SWLM ThreadedServer on port " + str(swm.PORT_SWLM))
t.start() # this blocks until keyboardinterrupt
logger.info("SWLM rpyc service stopped.")

# doesn't reach here util the script ends.
