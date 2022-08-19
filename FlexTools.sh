#!/bin/bash
# Be sure to set execute permission for the script.

# Configure how to call python here:
CALLPYTHON=python

# Configure the prefix to the path where FieldWorks is installed.
# /usr is the default for installing via the apt package manager on Ubuntu:
prefix=/usr

# In order to function correctly on Linux,
# we need to source a shell script (environ), which
# erases the path and several other environment variables.
# This function is called after the variables needed by FLEx
# are sourced in order to reset any variables needed by
# the caller which were erased.
resetenviron() {
    echo "Resetting environment"
}


# The following is adapted from the run-app shell script
# used to run an installed version of FLEx on Linux.
scriptdir=$(/bin/pwd)
lib=$prefix/lib/fieldworks
share=$prefix/share/fieldworks
sharedWsRoot=/var/lib/fieldworks
sharedWs=$sharedWsRoot/SIL/WritingSystemStore

# "$share/setup-user"

cd "$lib"; RUNMODE="INSTALLED" . environ;
cd $scriptdir

# reset environment as defined above
resetenviron

exec $CALLPYTHON FlexTools/FLExTools.py DEBUG
