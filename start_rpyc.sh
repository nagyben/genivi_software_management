#!/bin/bash

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

export PIDFILE=/tmp/swm_pidlist
echo $PIDFILE

rm -f $PIDFILE

export PYTHONPATH="/home/ben/Documents/genivi_software_management"

gnome-terminal --geometry 60x15+0+0 -x bash -c "echo \$BASHPID >> $PIDFILE; echo -ne \"\033]0;Package Manager\007\";python package_manager/package_manager.py; read x" &
gnome-terminal --geometry 60x15+0+400 -x bash -c "echo \$BASHPID >> $PIDFILE; echo -ne \"\033]0;Partition Manager\007\"; python partition_manager/partition_manager.py; read x" &
gnome-terminal --geometry 60x15+0+800 -x bash -c "echo \$BASHPID >> $PIDFILE; echo -ne \"\033]0;Module Loader ECU1\007\"; python module_loader_ecu1/module_loader_ecu1.py; read x" &
gnome-terminal --geometry 60x15+630+0 -x bash -c "echo \$BASHPID >> $PIDFILE; echo -ne \"\033]0;Software Loading Manager\007\"; python software_loading_manager/software_loading_manager.py; read x" &
gnome-terminal --geometry 60x15+630+400 -x bash -c "echo \$BASHPID >> $PIDFILE; echo -ne \"\033]0;Lifecycle Manager\007\"; python lifecycle_manager/lifecycle_manager.py; read x" &
gnome-terminal --geometry 60x15+630+800 -x bash -c "echo \$BASHPID >> $PIDFILE; echo -ne \"\033]0;HMI\007\"; python hmi/hmi.py; read x" &
gnome-terminal --geometry 60x15+1200+0 -x bash -c "echo \$BASHPID >> $PIDFILE; echo -ne \"\033]0;SOTA Client\007\"; python sota_client/sota_client.py -u sample_app_1.2.3 -i ./sample_update.upd -s xxx -d \"Sample Update Description\"; read x" &
#gnome-terminal --geometry 60x15+1200+400 -x bash -c "echo \$BASHPID >> $PIDFILE; echo -ne \"\033]0;Initializer\007\"; python initializer.py; read x" &

echo "Press Enter shut down Software Manager"

read x
killswm
