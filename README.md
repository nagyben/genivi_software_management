
Copyright (C) 2014-2015 Jaguar Land Rover

This document is licensed under Creative Commons
Attribution-ShareAlike 4.0 International.

# GENIVI SOFTWARE MANAGEMENT - PROOF OF CONCEPT #
This directory contains a set of python components that are used to
explore the API between the components forming the Software Management
system.

The components are outlined in the image below

![SWM Layout](https://github.com/magnusfeuer/genivi_software_management/raw/master/swm_illustration.png)
The components are as follows:

See the GENIVI SWLM specification for details on use cases, features, etc.

# ACRONYMS

Acronym   | Description
--------- | -----------
SWM       | Software Management
SC        | Sota Client
SWLM       | Software Loading Managent
PkgMgr    | Package Manager
PartMgr   | Partition Manager
ML        | Module Loader
HMI       | Human Machine Interface
LCMgr     | Life Cycle Manager
LocMedMgr | Local Media Manager

# TODO
1. **Implement get installed packages use case**<br>
   ```module_loader_ecu1.py``` needs to correctly implement ```get_module_firmware_version()```.
   ```package_manager.py``` needs to correctly implement ```get_installed_packages()```.
   ```software_loading_manager.py``` needs to implement ```get_installed_software()```, which means
   invoking ```package_manager.get_installed_packages()``` and ```get_module_firmware_version()```
   of each module loader instance. There is today no tracking in ```software_loading_manager.py```
   of deployed module loaders. Maybe extend ```SoftwareOperation.operation_descriptor```?

2. **Implement blacklists**<br>
    PackMgr ```install_package()``` and ```update_package()```
	needs to verify that the package in the ```image_path``` argument
	is not present in the list of banned packages in the
	```blacklist``` argument.<br><br>
	ML's ```flash_firmware()``` needs to run a SHA256 checksum
	on the image pointed to by ```image_path``` and verify that the sum
	is not present in the provided ```blacklist``` argument.<br><br>
	PartMgr ```write_disk_partition()``` and ```patch_disk_partition```
	needs to run a SHA256 checksum on the image pointed to by
	```image_path``` and verify that the sum is not present in the
	provided ```blacklist``` argument.<br>
	The blacklist needs to be persistent.

3. **Validate update available signature**<br>
   SWLM's ```update_available()``` implementation needs to be extended
   to validate that the ```signature``` argument matches the
   ```update_id``` argument to ensure that this is not a spoofed
   update available call sent from a malicious server to SC.  The
   ```signature``` is generated by<br> ```echo $UPDATE_ID | openssl
   dgst -sha256 -sign private_key | base64```<br>
   Public key needs to be read and used.

4. **Validate image**<br>
   SWLM's ```download_complete()``` implementation needs to be
   extended to validate that the image pointed to by
   ```update_image``` argument matches the ```signature``` argument to
   authenticate the image. The signature is generated by: ````openssl
   dgst -sha256 -sign priv_key.pem $image_path | base64```

5. **Create signing scripts and basic key management**<br>
   The ```create_update_image.sh``` script needs to create signatures
   and make sure that they can be used by ```sota_client.py```

6. **Expand use case testing**<br>
   There are many use case variants not tested today. A tesiting update
   should be created to provide a better test footprint.

7. **Implement LocMedMgr use case**<br>
   A LocMedMgr PoC component needs to be connected that
   simulated local media connect/mount, and disconect/unmount.
   LocMedMgr should feed the given events into to SWLM.
   SWLM needs to receive the mount/unmount event and execute the
   LocMedMgr update use case (chapter 6.4 in the SWM spec).

8. **Implement abort download**<br>
   ```software_loading_manager.py``` needs to implenent
   ```abort_download()``` as specified by the "SC Abort Download" use
   case described in chpater 6.2 of the SWM spec.

9. **Act both on SC- and manifest-provided user confirmation request**<br>
    Today the SC will include a ```request_confirmation``` flag in its
	```update_available()``` call to SWLM, specifying if the user
	should be queried prior to initating the download.  This does not
	work in the "LocMedMgr update" use case where the download stage
	is not applicable. Instead, the manifest file's
	```get_user_confirmation``` flag should be inspected by
	```manifest_processor.py``` to check if a confirmation is
	required. The ```get_user_confirmation``` flag is correctly
	specified in the SWLM spec, but the PoC code does not use it.

10.  **Implement the allow downgrade flag**<br>
    When SWLM sends an ```upgrade_package``` to PackMgr, the
    ```allow_downgrade``` flag needs to be implemented, checking
	if there is a newer version than the upgrade already installed.<br>
	The same flag needs to be implemented in ML as well.

11. **Implement parallel software operations**<br>
    The ```parallel``` JSON element inside the manifest file needs to
    be implemented by ```manifest_processor.py```. See chapter 5.3.8 and
	the ```operations[].parallel``` entry in Table 9.

12. **Integrate systemd emulator**<br>
    The current ```lifecycle_manager.py``` needs to be renamed to ```systemd_emulator.py```
    and implement the appropriate ```StartUnit()``` and ```StopUnit``` callas.


# RUNNING THE EXAMPLE ON NGI 1.0

This example assumes the user has access to a rig or a vehicle and knows how to start an SSH session with the IMC.

## Install python and rpyc
Make sure Python 2.7 is installed. **The Software Manager does not work with Python 3.x**

Copy the `rpyc` directory and its contents to `/usr/local/lib/python2.7/dist-packages/rpyc`. Create the folders if necessary.

## Launch SWLM components
In a terminal (through serial communications or SSH), as root, run `./start_rpyc_imc.sh`. **You must run this as root**.

This spawns the following Python processes:
1. `package_manager/package_manager.py`
2. `partition_manager/partition_manager.py`
3. `module_loader_ecu1/module_loader_ecu1.py`
4. `software_loading_manager/software_loading_manager.py`
5. `lifecycle_manager/lifecycle_manager.py`
6. `hmi/hmi.py`

These processes listen on localhost ports which are defined in `common/swm.py`. This is how RPyC carries out interprocess communication.

## Launch SOTA Client
In a separate terminal, as root, run `/.start_sota_client.sh`. This will count down for 5 seconds and begin the software-over-the-air demo update. When the operation is complete, the terminal window will display a summary.

## Inspect the log files
The log files are named after each SWLM component and are collected in the `logs/` folder contained in the same directory as the `start_sota_client.sh` script.

## Troubleshooting
### Error 98 address already in use
This error happens if SWLM components are already running. If the processes did not end properly, run

`ps aux | grep python`

Manually `kill -9 <PID>` where `<PID>` is the process ID(s) from the previous command.

# RUNNING THE CODE ON UBUNTU 14.10 AND 15.10

## Install python and add ons.

Make sure you have Python 2.7 (or later 2.X) installed.

Install the necessary python libraries

    sudo apt-get install python-gtk2


## Launch SWM components
In a terminal window, run a fully automated demo using:

    sudo sh start_swm.sh -r

```sudo``` is needed since the sample_update.upd file is a squashfs image that needs to be mounted.

```-r``` Specifies that the database storing already processed software operations (hosted in an update) should
be reset. If that is not done, subsequent runs will all return "Already processed"

```-i``` Does not start the sota_client.py, but instead prints
instruction on how to do so. This allows the user to run SC manually
and control the actions.

Each launched component will get their own terminal window.

## Watch execution
The system will execute the manifest from ```sample_update/update_manifest.json```, stored in the
```sample_update.upd``` squashfs image of the ```sample_update``` directory.

During the execution the HMI window will show an overall progress bar and a progress bar for each
software operation carried out.

The SWLM window will give a running log on what is going on.

All other windows will show progress bars as they are being invoked by
SWLM as it processes the manifest file.

## View installation report
The installation report will be displayed both by SC and HMI.

## Terminate demo
In the window where ```start_swm.sh``` was executed, press enter or ctrl-c.

## Sota client usage.

Usage:

    export PYTHONPATH="${PWD}/common/
	cd sota_client
    python sota_cliuent.py -u <update_id> -i <image_file> -d <description> -s <signature> [-c]

    -u update_id         Pacakage id string. Default: 'media_player_1_2_3'
    -i image_file        Path to update squashfs image.
    -s signature         RSA encrypted sha256um of image_file. (Not currently used)
    -c                   Request user confirmation.
    -d description       Description of update.

Example:

    export PYTHONPATH="${PWD}/common/
	cd sota_client
    python sota_client.py -u boot_loader_2.10.9 -i boot_loader.img -s 2889ee...4db0ed22cdb8f4e -c


# CREATING UPDATES

Please note that squashfs-tools needs to be installed prior to creating an update:

```sudo apt-get install squashfs-tools```

Create a new or modified update image with the following command:

```sh create_update_image.sh  -d sample_update -o sample_update.upd```

See SWM specification and ```software_loading_manager/manifest.py``` for details
on how to edit ```sample_update/update_manifest.json```.

The resulting image, ```sample_update.upd``` is provided as an argument to
```sota_client.py```. See ```start_swm.sh``` for details.


# SYSTEM DESCRIPTION

## SOTA Client - SC  [sota\_client/sota_client.py] ##

*NOTE: The SOTA Client also acts as a Diagnostic Tools Manager since
their use cases are identical*

SC simulator, to be replaced by the real GENIVI Sota Client developed
by Advanced Telematic Systems, is a command line tool that launches
the SWM use cases.

The SC simulator has the following features

1. **Notify SWM of available updates**<br>
   A notification about the available package, specified at the command line,
   will be sent to SWLM for user confirmation.

2. **Download the package**<br>
   Once a confirmation has been received from SWLM, SC will be asked by SWLM
   to initiate the download of the package. The download will be simulated
   with a 5 second progress bar.

3. **Send the package for processing**<br>
   Once the download has completed, the package is sent by SC to SWLM for processing.

4. **Handle installation report**<br>
   Once the package operation has completed, SWLM will forward an installation report to SC,
   which will present it as output before exitin.

5. **Get installed packages**<br>
   A separate use case allows the command line to request all currently installed
   packages in PkgMgr, PartMgr, or ML.

## Software Loading Manager - SWLM [software\_loading\_manager/*.py] ##
SWLM coordinates all use cases in SWM. SC Initiates these use cases
through command line parameters

SWLM has the following features

1. **Retrieve user approval for packages**<br>
   When a package notification is received from SC, the notification
   will be forwarded to HMI for a user approval.

2. **Signal SC to start download**<br>
   When SWLM receives a package confirmation from HMI, the SC will be
   signalled to initiate the download.

3. **Process downloaded packages**<br>
   Once a download is complete, SC will send a process package command
   to SWLM.  SWLM will forward the command to the approrpiate target,
   which can be PartMgr for partition operations, PackMgr fo package
   manager, or ML for the module loader

4. **Handle installation report**<br>
   When a target has processed a package it will wend back a
   installation report to SWLM, which will forward it to HMI, to inform
   the user, and SC, to inform the server.

5. **Get installed packages**<br>
   When a get installed packages command is received from SC, it will
   be forwarded to the package manaager to retrieve a list of all
   installed packages.


## Human Machine Interface - HMI [hmi/hmi.py] ##
HMI is responsible for reqtrieving a user approval (or decline) on
a package installation, and to show the user the result of a package
operation.

HMI has the following features

1. **Retrieve user approval for packages**<br>
   SWLM will send a package notification to HMI, which will ask the
   user if the package operation is to be carried out or not.  The
   user input (approve or decline) is forwarded as a package
   confirmation to SWLM

2. **Show update progress**<br>
   SWLM will inform HMI when a new manifest is being processed, and
   when a new software operation within that manifest is being
   processed.  This allows the HMI to continuously display information
   and progress bars as the update is carried out.

3. **Show package operation result**<br>
   Once a package operation has been carried out by PkgMgr, PartMgr,
   or ML, the result will be forwarded to HMI to inform the ser.


## Package Manager - PackMgr [package_manager/package\_manager.py] ##
PackMgr is responsible for processing packages forwarded to it by SWLM.
It can also report all currently installed packages.

PackMgr has the following features

1. **Install package**<br>
   SWLM will send a install a package command, which will simulate
   package install and then send back a installation report.

2. **Upgrade package**<br>
   SWLM will send an upgrade a package command, which will simulate
   package upgrade and then send back a installation report.

3. **Remove package**<br>
   SWLM will send a remove a package command, which will simulate
   package removal and then send back a installation report.

4. **Get installed packages**<br>
   PackMgr will send back a static list of currently installed
   packages.


## Partition Manager - PartMgr [partition\_manager.py] ##
PartMgr is responsible for processing packages forwarded to it by SWLM.
It can also report all currently installed packages.

PartMgr has the following features

1. **Create Partition**<br>
   SWLM will send a create partition command, which will simulate
   partition creation and then send back a installation report.

2. **Delete Partition**<br>
   SWLM will send a delete partition command, which will simulate
   partition deletion and then send back a installation report.

3. **Resize Partition**<br>
   SWLM will send a resize partition command, which will simulate
   partition resizing and then send back a installation report.

4. **Write Partition**<br>
   SWLM will send a resize partition command, which will simulate
   partition writing and then send back a installation report.

5. **Patch Partition**<br>
   SWLM will send a resize partition command, which will simulate
   partition binary delta applicaiton and then send back a
   installation report.


## Module Loader - ML [module\_loader\_ecu1/module\_loader\_ecu1.py] ##
ML, which can have multiple different instances for different ECUs
(SiriusXM, Telematics Control Unit, Body Control Unit, etc), is
responsible for reflashing external modules through CAN or other
in-vehicle networks.

ML has the following features

1. **Flash module firmware**<br>
   SWLM will send a flash module firmwar command, which will simulate
   module flashing and then send back a installation report.

2. **Get installed packages**<br>
   ML will send back a static list of currently installed
   flash images in the module managed by ML.


## Lifecycle manager - LCMgr  [lifecycle\_manager/lifecycle_manager.py] ##

LCMgr manager (to be replaced by systemd and Node State Managerin
production) simulates a system component that can start and stop
software entitites that are about to be affected by an update
operation.

LCMgr has the following features.

ML has the following features

1. **Start components**<br>
   SWLM will send a start_component, which will simulate
   component(s) start.

2. **Stop components**<br>
   SWLM will send a start_component, which will simulate
   component(s) stop.

3. **Reboot system**<br>
   SWLM will send a reboot command, which will simulate
   system reboot.
