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

#
# Package manager service
#

class PackageManager(object):
    def install_package(self,
                        transaction_id,
                        image_path,
                        blacklisted_packages):

        try:
            print "Package Manager: Install Package"
            print "  Operation Transaction ID: {}".format(transaction_id)
            print "  Image Path:               {}".format(image_path)
            #print "  Blacklisted packages:     {}".format(blacklisted_packages)
            print "---"

            # Simulate install
            #TODO: implement install package routine
            # I think the below will work
            subprocess.check_call("rpm -ivh --force {}".format(image_path), shell=True)
            subprocess.check_call("sync", shell=True)

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

        except subprocess.CalledProcessError as e:
            print "install_package() CalledProcessError returncode: {}".format(e.returncode)
            print str(e)
            swm.send_operation_result(transaction_id,
                                      swm.SWM_RES_INTERNAL_ERROR,
                                      "Internal_error: {}".format(e))

        except Exception as e:
            print "install_package() Exception: {}".format(e)
            # traceback.print_exc()
            print str(e)
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
            print "Package Manager: Upgrade package"
            print "  Operation Transaction ID: {}".format(transaction_id)
            print "  Image Path:               {}".format(image_path)
            print "  Allow downgrade:          {}".format(allow_downgrade)
            print "  Blacklisted packages:     {}".format(blacklisted_packages)
            print "---"

            # Simulate install
            #TODO: implement upgrade_package routine
            #I think the below will work
            subprocess.check_call("rpm -Uvh --force --replacefiles {}".format(image_path), shell=True)
            subprocess.check_call("sync", shell=True)

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

        except subprocess.CalledProcessError as e:
            print "upgrade_package() CalledProcessError returncode: {}".format(e.returncode)
            print str(e)
            swm.send_operation_result(transaction_id,
                                      swm.SWM_RES_INTERNAL_ERROR,
                                      "Internal_error: {}".format(e))

        except Exception as e:
            print "upgrade_package() Exception: {}".format(e)
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
            print "Package Manager: Remove package"
            print "  Operation Transaction ID: {}".format(transaction_id)
            print "  Package ID:               {}".format(package_id)
            print "---"

            # Simulate remove
            #TODO: test remove_package logic
            subprocess.check_call("rpm -e {}".format(package_id), shell=True)
            subprocess.check_call("sync", shell=True)

            print "Removing package: {} (5 sec)".format(package_id)
            for i in xrange(1,50):
                sys.stdout.write('.')
                sys.stdout.flush()
                time.sleep(0.1)
            print
            print "Done"
            swm.send_operation_result(transaction_id,
                                      swm.SWM_RES_OK,
                                      "Removal successful. Package_id: {}".format(package_id))

        except subprocess.CalledProcessError as e:
            print "remove_package() CalledProcessError returncode: {}".format(e.returncode)
            print str(e)
            swm.send_operation_result(transaction_id,
                                      swm.SWM_RES_INTERNAL_ERROR,
                                      "Internal_error: {}".format(e))

        except Exception as e:
            print "remove_package() Exception: {}".format(e)
            #traceback.print_exc()
            e.print_exc()
            swm.send_operation_result(transaction_id,
                                      swm.SWM_RES_INTERNAL_ERROR,
                                      "Internal_error: {}".format(e))
        return None

    def get_installed_packages(self):
        print "Got get_installed_packages()"
        return [ 'bluez_driver_1.2.2', 'bluez_apps_2.4.4' ]


class PkgMgrService(rpyc.Service):
    def on_connect(self):
        print "A client connected"

    def on_disconnect(self):
        print "A client disconnected"

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
print "Package Manager."
print

print "Initializing PackageManager..."
PackMgr = PackageManager()

from rpyc.utils.server import ThreadedServer
t = ThreadedServer(PkgMgrService, port = swm.PORT_PACKMGR)
print "Starting PackageManager ThreadedServer service on port " + str(swm.PORT_PACKMGR)
t.start()
