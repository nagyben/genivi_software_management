# (c) 2015 - Jaguar Land Rover.
#
# Mozilla Public License 2.0

#
# Result constants
#
import traceback
import rpyc
import logging

SWM_RES_OK = 0
SWM_RES_ALREADY_PROCESSED = 1
SWM_RES_DEPENDENCY_FAILURE = 2
SWM_RES_VALIDATION_FAILED = 3
SWM_RES_INSTALL_FAILED = 4
SWM_RES_UPGRADE_FAILIED = 5
SWM_RES_REMOVAL_FAILED = 6
SWM_RES_FLASH_FAILED = 7
SWM_RES_CREATE_PARTITION_FAILED = 8
SWM_RES_DELETE_PARTITION_FAILED = 9
SWM_RES_RESIZE_PARTITION_FAILED = 10
SWM_RES_WRITE_PARTITION_FAILED = 11
SWM_RES_PATCH_PARTITION_FAILED = 12
SWM_RES_USER_DECLINED = 13
SWM_RES_OPERATION_BLACKLISTED = 14
SWM_RES_DISK_FULL = 15
SWM_RES_NOT_FOUND = 16
SWM_RES_OLD_VERSION = 17
SWM_RES_INTERNAL_ERROR = 18
SWM_RES_GENERAL_ERROR = 19
_SWM_RES_FIRST_UNUSED = 20

PORT_SC         = 50001
PORT_SWLM       = 50002
PORT_PARTMGR    = 50003
PORT_PACKMGR    = 50004
PORT_ECU1       = 50005
PORT_LCMGR      = 50006
PORT_HMI        = 50007

sc_rpyc         = 0
swlm_rpyc       = 0
partmgr_rpyc    = 0
packmgr_rpyc    = 0
ecu1_rpyc       = 0
lcmgr_rpyc      = 0
hmi_rpyc        = 0

# configure logging
logFormatter = logging.Formatter("[%(asctime)s] swm - %(levelname)s - %(message)s")
logger = logging.getLogger("swm")
logger.setLevel(logging.DEBUG)

fileHandler = logging.FileHandler("logs/{}.log".format("swm"))
fileHandler.setFormatter(logFormatter)
logger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
logger.addHandler(consoleHandler)


def result(operation_id, code, text):
    if code < SWM_RES_OK or code >= _SWM_RES_FIRST_UNUSED:
        code = SWM_RES_GENERAL_ERROR

    return {
        'id': operation_id, #dbus.String(operation_id, variant_level=1),
        'result_code': code, #dbus.Int32(code, variant_level=1),
        'result_text': text #dbus.String(text, variant_level=1)
    }

def rpyc_method(port, method, *arguments):
    try:
        logger.info("Connecting to rpyc service on localhost at port " + str(port))
        rpyc_remote = rpyc.connect("localhost", port)
        rpyc_service_name = rpyc_remote.root.get_service_name()
        logger.info("Connected to " + str(rpyc_service_name))
        argslist = ", ".join(str(arg) for arg in arguments)
        logger.info("Calling " + str(rpyc_service_name) + "." + str(method) + "(" + argslist + ")")

        # find the method name by introspection and call it using the arguments (if any exist)
        async_func = rpyc.async(getattr(rpyc_remote.root, str(method)))
        async_func(*arguments)
    except Exception as e:
        logger.info(str(e))
        traceback.print_exc()

    return None

def send_operation_result(transaction_id, result_code, result_text):
    #
    # Send back operation result.
    # Software Loading Manager will distribute the report to all interested parties.
    #

    swlm_rpyc = rpyc.connect("localhost", PORT_SWLM)
    swlm_rpyc.root.exposed_operation_result(transaction_id, result_code, result_text)

    return None
