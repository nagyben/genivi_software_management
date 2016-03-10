# (C) 2015 - Jaguar Land Rover.
#
# Mozilla Public License 2.0
#
# Python dbus service that faces SOTA interface
# of Software Loading manager.

import getopt
import sys
import time
import common.swm as swm
import traceback
from threading import Thread
import os

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

# Default command line arguments
update_id='media_player_1_2_3'
description='Media Player Update'
signature='d2889ee6bc1fe1f3d7c5cdaca78384776bf437b7c6ca4db0e2c8b1d22cdb8f4e'
update_file=''
active=True

class SOTAClient(object):
    def __init__(self, image_file, signature):
        # Store where we have the image file
        self.image_file = image_file

        # Store signature
        self.signature = signature

    def initiate_download(self,
                          update_id):
        global target
        global command
        global size
        global description
        global vendor
        global path
        logger.info("Got initiate_download")
        logger.info("  ID:     {}".format(update_id))
        logger.info("---")

        #  Simulate download
        logger.info("Downloading")
        for i in xrange(1,10):
            sys.stdout.write('.')
            sys.stdout.flush()
            time.sleep(0.1)
        print
        logger.info("Done.")

        swlm_rpyc = rpyc.connect("localhost", swm.PORT_SWLM)
        swlm_rpyc.root.download_complete(self.image_file, self.signature)

        return None

    def update_report(self,
                      update_id,
                      results):
        global active
        logger.info("Update report")
        logger.info("  ID:          {}".format(update_id))
        for result in results:
            logger.info("    operation_id: {}".format(result['id']))
            logger.info("    code:         {}".format(result['result_code']))
            logger.info("    text:         {}".format(result['result_text']))
            logger.info("  ---")
        logger.info("---")
        active = False
        return None

class SOTAClientService(rpyc.Service):
    def on_connect(self):
        # code runs when connection is created
        logger.info("Client connected")

    def on_disconnect(self):
        # code runs when the connection has closed
        logger.info("Client disconnected")

    def exposed_initiate_download(self, update_id):
        """ function to expose initiate_download to RPyC
        """
        return SC.initiate_download(update_id)

    def exposed_update_report(self, update_id, results):
        """ function to expose update_report to RPyC
        """
        return SC.update_report(update_id, results)

def usage():
    print "Usage:", sys.argv[0], "-u update_id -i image_file -d description \\"
    print "                       -s signature [-c]"
    print
    print "  -u update_id         Pacakage id string. Default: 'media_player_1_2_3'"
    print "  -i image_file        Path to update squashfs image."
    print "  -s signature         RSA encrypted sha256um of image_file."
    print "  -c                   Request user confirmation."
    print "  -d description       Description of update."
    print
    print "Example:", sys.argv[0],"-u boot_loader_2.10.9\\"
    print "                        -i boot_loader.img  \\"
    print "                        -s 2889ee...4db0ed22cdb8f4e -c"
    sys.exit(255)

def threaded_start():
    from rpyc.utils.server import ThreadedServer
    t = ThreadedServer(SOTAClientService, port = swm.PORT_SC)
    logger.info("Launching SOTA Client ThreadedServer on port " + str(swm.PORT_SC))
    t.start()

# === entry point ===
try:
    opts, args= getopt.getopt(sys.argv[1:], "u:d:i:s:c")
except getopt.GetoptError as e:
    logger.exception("Could not parse arguments.")
    usage()

image_file = None

request_confirmation = False
for o, a in opts:
    if o == "-u":
        update_id = a
    elif o == "-d":
        description = a
    elif o == "-i":
        image_file = a
    elif o == "-s":
        signature = a
    elif o == "-c":
        request_confirmation = True
    else:
        logger.warning("Unknown option: {}".format(o))
        usage()

if not image_file:
    print
    logger.warning("No -i image_file provided.")
    print
    usage()

# Can we open the confirmation file?
try:
    image_desc = open(image_file, "r")
except IOError as e:
    logger.exception("Could not open {} for reading: {}".format(image_file, e))
    sys.exit(255)

image_desc.close()

logger.info("Will simulate downloaded update:")
logger.info("Update ID:          {}".format(update_id))
logger.info("Description:        {}".format(description))
logger.info("Image file:         {}".format(image_file))
logger.info("User Confirmation:  {}".format(request_confirmation))

try:

    # USE CASE
    #
    # This sota_client will send a update_available() call to the
    # software loading manager (SLM).
    #
    # If requested, SWLM will pop an operation confirmation dialog on the HMI.
    #
    # If confirmed, SWLM will make an initiate_download() callback to
    # this sota_client.
    #
    # The sota_client will, on simulated download completion, make a
    # download_complete() call to the SLM to indicate that the update is
    # ready to be processed.
    #
    # The SLM will mount the provided image file as a loopback file system
    # and execute its update_manifest.json file. Each software operation in
    # the manifest file will be fanned out to its correct target (PackMgr,
    # ML, PartMgr)
    #
    # Once the update has been processed by SLM, an update operation
    # report will be sent back to SC and HMI.

    logger.info("Initializing SOTA Client")
    SC = SOTAClient(image_file, signature)

    thread = Thread(target = threaded_start)
    thread.start()

    logger.info("Starting in 5")
    for i in reversed(range(1, 5)):
        logger.info(str(i) + "...")
        time.sleep(1)

    logger.info("Starting operation...")
    swlm_rpyc = rpyc.connect("localhost", swm.PORT_SWLM)
    swlm_rpyc.root.exposed_update_available(update_id, description, signature, request_confirmation)

    thread.join()



except KeyboardInterrupt:
    logger.info('Interrupted')
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)

except Exception as e:
    logger.exception("Exception: {}".format(e))
    traceback.print_exc()
