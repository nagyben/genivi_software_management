#!/bin/bash
#
# (c) 2015 - Jaguar Land Rover.
#
# Mozilla Public License 2.0
#
# Ubuntu Software Manager Loader launch script
#

PIDFILE=/tmp/swm_pidlist

killswm () {
	for i in $(cat $PIDFILE); do
		kill $i
	done
	exit 0
}

if [ "$(id -u)" != "0" ]
then
	echo "How about sudo..."
	exit 1
fi

usage() {
	echo "Usage: ${0} [-r] [-i]"
	echo "  -r    Reset completed operation database"
	echo "  -i    Run in interactive mode. Start sota_client separately"
	exit 255
}

#SWLM_ARG=""
#INTERACTIVE=false
#while getopts ":ri" opt; do
#  case $opt in
#    r)
#		SWLM_ARG="-r"
#		;;
#	i)
#		INTERACTIVE="true"
#		;;
#    \?)
#      echo "Invalid option: -$OPTARG" >&2
#      ;;
#  esac
#done

export PYTHONPATH=$PWD
rm -f $PIDFILE

gnome-terminal --geometry 60x15+0+0 -x bash -c "echo \$BASHPID >> $PIDFILE; echo -ne \"\033]0;Package Manager\007\";python package_manager/package_manager.py; read x" &
gnome-terminal --geometry 60x15+0+400 -x bash -c "echo \$BASHPID >> $PIDFILE; echo -ne \"\033]0;Partition Manager\007\"; python partition_manager/partition_manager.py; read x" &
gnome-terminal --geometry 60x15+0+800 -x bash -c "echo \$BASHPID >> $PIDFILE; echo -ne \"\033]0;Module Loader ECU1\007\"; python module_loader_ecu1/module_loader_ecu1.py; read x" &
gnome-terminal --geometry 60x15+630+0 -x bash -c "echo \$BASHPID >> $PIDFILE; echo -ne \"\033]0;Software Loading Manager\007\"; python software_loading_manager/software_loading_manager.py; read x" &
gnome-terminal --geometry 60x15+630+400 -x bash -c "echo \$BASHPID >> $PIDFILE; echo -ne \"\033]0;Lifecycle Manager\007\"; python lifecycle_manager/lifecycle_manager.py; read x" &
gnome-terminal --geometry 60x15+630+800 -x bash -c "echo \$BASHPID >> $PIDFILE; echo -ne \"\033]0;HMI\007\"; python hmi/hmi.py; read x" &

#trap killswm INT

#if [ "${INTERACTIVE}" = "false" ]
#then
#	cd sota_client
#	echo "Running SOTA client with HMI user confirmation turned off. Use -c to turn on"
#	python sota_client.py -u sample_app_1.2.3 -i ../sample_update.upd -s xxx -d "Sample Update Description"
#	read x
#	killswm
#	exit 0
#fi

echo "Please run"
echo
echo "   cd sota_client"
echo "   sudo PYTHONPATH=\"\${PWD}/../common/\" python sota_client.py -u sample_app_1.2.3 -c -i ../sample_update.upd -s xxx -d \"Sample Update Description\""
echo
echo "to start package use case."
echo
echo "Press Enter shut down Software Manager"

read x
killswm
