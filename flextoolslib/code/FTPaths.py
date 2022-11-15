#
#   Project: FlexTools
#   Module:  FTPaths
#
#   Global definitions of data paths for FLExTools
#
#   Craig Farrow
#   Mar 2012
#

import os

# Create absolute paths relative to this directory
MODULES_PATH = os.path.join(os.path.dirname(__file__), "Modules")
COLLECTIONS_PATH = os.path.join(os.path.dirname(__file__), "Collections")
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "flextools.ini")
