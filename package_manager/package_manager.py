# (c) 2015 - Jaguar Land Rover.
#
# Mozilla Public License 2.0
#
# Python-based package manager PoC


import sys
import time
import common.swm as swm
import subprocess

import rpyc

import logging

# configure logging
logFormatter = logging.Formatter("[%(asctime)s] PACKMGR - %(levelname)s - %(message)s")
logger = logging.getLogger("PACKMGR")
logger.setLevel(logging.DEBUG)

fileHandler = logging.FileHandler("logs/{}.log".format("package_manager"))
fileHandler.setFormatter(logFormatter)
logger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
logger.addHandler(consoleHandler)

#
# Package manager service
#

class PackageManager(object):
    def install_package(self,
                        transaction_id,
                        image_path,
                        blacklisted_packages):

        try:
            logger.info("Package Manager: Install Package")
            logger.info("  Operation Transaction ID: {}".format(transaction_id))
            logger.info("  Image Path:               {}".format(image_path))
            #logger.info("  Blacklisted packages:     {}".format(blacklisted_packages))
            logger.info("---")

            # Simulate install
            #TODO: implement install package routine
            # I think the below will work
            subprocess.check_call("rpm -ivh --force {}".format(image_path), shell=True)
            subprocess.check_call("sync", shell=True)

            logger.info("Intalling package: {} (5 sec)".format(image_path))
            for i in xrange(1,50):
                sys.stdout.write('.')
                sys.stdout.flush()
                time.sleep(0.1)
            print
            logger.info("Done")
            swm.send_operation_result(transaction_id,
                                      swm.SWM_RES_OK,
                                      "Installation successful. Path: {}".format(image_path))

        except subprocess.CalledProcessError as e:
            logger.exception("install_package() CalledProcessError returncode: {}".format(e.returncode))
            logger.exception(str(e))
            swm.send_operation_result(transaction_id,
                                      swm.SWM_RES_INTERNAL_ERROR,
                                      "Internal_error: {}".format(e))

        except Exception as e:
            logger.exception("install_package() Exception: {}".format(e))
            # traceback.print_exc()
            logger.exception(str(e))
            swm.send_operation_result(transaction_id,
                                      swm.SWM_RES_INTERNAL_ERROR,
                                      "Internal_error: {}".format(e))
        return None

    def upgrade_package(self,
                        transaction_id,
                        image_path,
                        blacklisted_packages,
                        allow_downgrade):

        try:
            logger.info("Package Manager: Upgrade package")
            logger.info("  Operation Transaction ID: {}".format(transaction_id))
            logger.info("  Image Path:               {}".format(image_path))
            logger.info("  Allow downgrade:          {}".format(allow_downgrade))
            logger.info("  Blacklisted packages:     {}".format(blacklisted_packages))
            logger.info("---")

            # Simulate install
            #TODO: implement upgrade_package routine
            #I think the below will work
            subprocess.check_call("rpm -Uvh --force --replacefiles {}".format(image_path), shell=True)
            subprocess.check_call("sync", shell=True)

            logger.info("Upgrading package: {} (5 sec)".format(image_path))
            for i in xrange(1,50):
                sys.stdout.write('.')
                sys.stdout.flush()
                time.sleep(0.1)
            print
            logger.info("Done")
            swm.send_operation_result(transaction_id,
                                      swm.SWM_RES_OK,
                                      "Upgrade successful. Path: {}".format(image_path))

        except subprocess.CalledProcessError as e:
            logger.exception("upgrade_package() CalledProcessError returncode: {}".format(e.returncode))
            logger.exception(str(e))
            swm.send_operation_result(transaction_id,
                                      swm.SWM_RES_INTERNAL_ERROR,
                                      "Internal_error: {}".format(e))

        except Exception as e:
            logger.exception("upgrade_package() Exception: {}".format(e))
            #traceback.print_exc()
            e.print_exc()
            swm.send_operation_result(transaction_id,
                                      swm.SWM_RES_INTERNAL_ERROR,
                                      "Internal_error: {}".format(e))
        return None

    def remove_package(self,
                       transaction_id,
                       package_id):
        try:
            logger.info("Package Manager: Remove package")
            logger.info("  Operation Transaction ID: {}".format(transaction_id))
            logger.info("  Package ID:               {}".format(package_id))
            logger.info("---")

            # Simulate remove
            #TODO: test remove_package logic
            subprocess.check_call("rpm -e {}".format(package_id), shell=True)
            subprocess.check_call("sync", shell=True)

            logger.info("Removing package: {} (5 sec)".format(package_id))
            for i in xrange(1,50):
                sys.stdout.write('.')
                sys.stdout.flush()
                time.sleep(0.1)
            print
            logger.info("Done")
            swm.send_operation_result(transaction_id,
                                      swm.SWM_RES_OK,
                                      "Removal successful. Package_id: {}".format(package_id))

        except subprocess.CalledProcessError as e:
            logger.exception("remove_package() CalledProcessError returncode: {}".format(e.returncode))
            logger.exception(str(e))
            swm.send_operation_result(transaction_id,
                                      swm.SWM_RES_INTERNAL_ERROR,
                                      "Internal_error: {}".format(e))

        except Exception as e:
            logger.exception("remove_package() Exception: {}".format(e))
            #traceback.print_exc()
            e.print_exc()
            swm.send_operation_result(transaction_id,
                                      swm.SWM_RES_INTERNAL_ERROR,
                                      "Internal_error: {}".format(e))
        return None

    def get_installed_packages(self):
        logger.info("Got get_installed_packages()")
        return [ 'bluez_driver_1.2.2', 'bluez_apps_2.4.4' ]


class PkgMgrService(rpyc.Service):
    def on_connect(self):
        logger.info("A client connected")

    def on_disconnect(self):
        logger.info("A client disconnected")

    def exposed_install_package(self, transaction_id, image_path, blacklisted_packages):
        """ function to expose install_pacakge over rpyc
        """
        return PackMgr.install_package(transaction_id, image_path, blacklisted_packages)

    def exposed_upgrade_pacakge(self, transaction_id, image_path, blacklisted_packages, allow_downgrade):
        """ function to expose upgrade_package over rpyc
        """
        return PackMgr.upgrade_package(transaction_id, image_path, blacklisted_packages, allow_downgrade)

    def exposed_remove_package(self, transaction_id, package_id):
        """ function to expose remove_package over rpyc
        """
        return PackMgr.remove_package(transaction_id, package_id)

    def exposed_get_installed_packages(self):
        """ function to expose get_installed_packages over rpyc
        """
        return PackMgr.get_installed_packages()

print
logger.info("Package Manager.")
print

logger.info("Initializing PackageManager...")
PackMgr = PackageManager()

from rpyc.utils.server import ThreadedServer
t = ThreadedServer(PkgMgrService, port = swm.PORT_PACKMGR)
logger.info("Starting PackageManager ThreadedServer service on port " + str(swm.PORT_PACKMGR))
t.start()
