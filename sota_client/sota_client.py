# (C) 2015 - Jaguar Land Rover.
#
# Mozilla Public License 2.0
#
# Python dbus service that faces SOTA interface
# of Software Loading manager.


#import gtk
#import dbus
#import dbus.service
#from dbus.mainloop.glib import DBusGMainLoop
import getopt
import sys
import time
import swm
import traceback
from threading import Thread

import rpyc

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
                          update_id,
                          send_reply,
                          send_error):
        global target
        global command
        global size
        global description
        global vendor
        global path
        print "Got initiate_download"
        print "  ID:     {}".format(update_id)
        print "---"

        #  Simulate download
        print "Downloading"
        for i in xrange(1,10):
            sys.stdout.write('.')
            sys.stdout.flush()
            time.sleep(0.1)
        print
        print "Done."

        swlm_rpyc = rpyc.connect("localhost", swm.PORT_SWLM)
        swlm_rpyc.root.download_complete(image_file, signature)

        return None

    def update_report(self,
                      update_id,
                      results):
        global active
        print "Update report"
        print "  ID:          {}".format(update_id)
        for result in results:
            print "    operation_id: {}".format(result['id'])
            print "    code:         {}".format(result['result_code'])
            print "    text:         {}".format(result['result_text'])
            print "  ---"
        print "---"
        active = False
        return None

class SOTAClientService(rpyc.Service):
    def on_connect(self):
        # code runs when connection is created
        print "Client connected"

    def on_disconnect(self):
        # code runs when the connection has closed
        print "Client disconnected"

    def exposed_initiate_download(self, update_id, send_reply, send_error):
        """ function to expose initiate_download to RPyC
        """
        return SC.initiate_download(update_id, send_reply, send_error)

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

# === entry point ===
try:
    opts, args= getopt.getopt(sys.argv[1:], "u:d:i:s:c")
except getopt.GetoptError:
    print "Could not parse arguments."
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
        print "Unknown option: {}".format(o)
        usage()

if not image_file:
    print
    print "No -i image_file provided."
    print
    usage()

# Can we open the confirmation file?
try:
    image_desc = open(image_file, "r")
except IOError as e:
    print "Could not open {} for reading: {}".format(image_file, e)
    sys.exit(255)

image_desc.close()

print "Will simulate downloaded update:"
print "Update ID:          {}".format(update_id)
print "Description:        {}".format(description)
print "Image file:         {}".format(image_file)
print "User Confirmation:  {}".format(request_confirmation)

try:
    #DBusGMainLoop(set_as_default=True)

    #sota_svc = SOTAClientService(image_file, signature)

    print "Initializing SOTA Client"
    SC = SOTAClient(image_file, signature)

    from rpyc.utils.server import ThreadedServer
    t = ThreadedServer(SOTAClientService, port = swm.PORT_SC)
    print "Launching SOTA Client ThreadedServer on port " + str(swm.PORT_SC)
    t.start()

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
    # Once the update has been processed by SLM, an u@dbus

    #swm.dbus_method('org.genivi.software_loading_manager', 'update_available',
    #                update_id, description, signature, request_confirmation)



    #active = True

    # Active will be set to false by installation_report()
    #while active:
    #    gtk.main_iteration()


except Exception as e:
    print "Exception: {}".format(e)
    traceback.print_exc()
