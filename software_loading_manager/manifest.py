# (c) 2015 - Jaguar Land Rover.
#
# Mozilla Public License 2.0
#
# Library to process updates



import json
from collections import deque
import software_operation
import common.swm as swm
import traceback

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
# Load and execute a single manifest
#
class Manifest:
    # There is a better way of doing this, but
    # this will work for now
    def __init__(self,
                 blacklisted_firmware,
                 blacklisted_packages,
                 blacklisted_partitions,
                 manifest_processor):
        #
        # The transaction we are waiting for a reply callback on
        #
        # FIXME: Multiple parallel transactions not supported,
        #        although the manifest file format does.
        #
        self.active_operation = None
        self.manifest_processor = manifest_processor
        self.mount_point = manifest_processor.mount_point

        # Store the blacklists to be injected as arguments
        # where the operation descriptor specifies it.
        self.blacklisted_partitions = blacklisted_partitions
        self.blacklisted_firmware = blacklisted_firmware
        self.blacklisted_packages = blacklisted_packages

        # Reset the update result
        self.operation_results = []

    # Load a manifest from a file
    def load_from_file(self, manifest_fname):
        logger.info("Manifest:load_from_file({}): Called.".format(manifest_fname))
        try:
            with open(manifest_fname, "r") as f:
                logger.info("Opened. Will load string")
                return self.load_from_string(f.read())

        except IOError as e:
            logger.exception("Could not open manifest {}: {}".format(manifest_fname, e))
            return False


    # Load a manifest from a string
    def load_from_string(self, manifest_string):

        logger.info("Manifest.load_from_string(): Called")
        try:
            manifest = json.loads(manifest_string)
        except ValueError as e:
            logger.exception("Manifest: Failed to parse JSON string: {}".format(e))
            return False

        # Retrieve top-level elements
        self.update_id = manifest.get('update_id', False)
        self.name = manifest.get('name', False)
        self.description = manifest.get('description', False)
        self.show_hmi_progress = manifest.get('show_hmi_progress', False)
        self.show_hmi_result = manifest.get('show_hmi_result', False)
        self.allow_downgrade = manifest.get('allow_downgrade', False)
        self.get_user_confirmation = manifest.get('get_user_confirmation', False)
        self.operations = deque()
        logger.info("Manifest.update_id:             {}".format(self.update_id))
        logger.info("Manifest.name:                  {}".format(self.name))
        logger.info("Manifest.description:           {}".format(self.description))
        logger.info("Manifest.get_user_confirmation: {}".format(self.get_user_confirmation))
        logger.info("Manifest.show_hmi_progress:     {}".format(self.show_hmi_progress))
        logger.info("Manifest.show_hmi_result:       {}".format(self.show_hmi_result))
        logger.info("Manifest.allow_downgrade:       {}".format(self.allow_downgrade))

        # Traverse all operations and create / load up a relevant
        # object for each one.
        try:
            for op in manifest.get('operations', []):

                # Grab opearation id.
                op_id = op.get('id', False)

                # Skip entire operation if operation_id is not defined.
                if not op_id:
                    logger.warning("Manifest operation is missing operation_id. Skipped")
                    continue

                # Check if this operation has already been executed
                if self.manifest_processor.is_operation_completed(op_id):
                    # Add the result code for the given operation id
                    self.operation_results.append(
                        swm.result(op_id,
                                   swm.SWM_RES_ALREADY_PROCESSED,
                                   "Operation already processed")
                        )

                    logger.warning("Software operation {} already completed. Deleted from manifest".format(op_id))
                    # Continue with the next operation
                    continue

                # Retrieve the class to instantiate for the given operation


                # Instantiate an object and feed it the manifest file
                # operation object so that the new object can initialize
                # itself correctly.
                try:
                    op_obj = software_operation.SoftwareOperation(self, op)
                except OperationException as e:
                    logger.exception("Could not process softare operation {}: {}\nSkipped".format(op_id, e))
                    return False

                # Add new object to operations we need to process
                self.operations.append(op_obj)
        except Exception as e:
            logger.exception("Manifest exception: {}".format(e))
            traceback.print_exc()
            return False

        # Check that we have all mandatory fields set
        if False in [ self.update_id, self.name, self.description ]:
            logger.warning("One of update_id, name, description, or operations not set")
            return False

        return True

    def start_next_operation(self):
        if len(self.operations) == 0:
            return False

        # Retrieve next operation to process.
        op = self.operations.popleft()

        transaction_id = self.manifest_processor.get_next_transaction_id()

        #
        # Invoke the software operation object, created by
        # the Manifest object
        #
        if op.send_transaction(transaction_id):
            # Store this as an active transaction for which we
            # are waiting on a callback reply.
            self.active_operation = op
            return True

        return False


    #
    # Check if this operation has already been executed.
    #
    def complete_transaction(self, transaction_id, result_code, result_text):
        # Check that we have an active transaction to
        # work with.
        if not self.active_operation:
            logger.warning("complete_transaction(): Warning: No active transaction for {}.".format(transaction_id))
            return False

        # We have completed this specific transaction
        # Store it so that we don't run it again on restart
        self.manifest_processor.add_completed_operation(self.active_operation.operation_id)

        #
        # Add the result code from a software operation to self
        # All operation results will be reported to SOTA.
        #
        self.operation_results.append(
            swm.result(
                self.active_operation.operation_id,
                result_code,
                result_text)
        )

        self.active_operation = None
        return True
