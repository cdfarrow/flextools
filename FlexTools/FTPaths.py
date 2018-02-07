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

# Make sure FlexLibs & CDFUtils are on the path (using .pth file in ..\)

import site
site.addsitedir(os.path.join(os.path.dirname(__file__), u"..\\"))

# Create absolute paths relative to this directory (where this file resides)

MODULES_PATH = os.path.join(os.path.dirname(__file__), u"Modules")
COLLECTIONS_PATH = os.path.join(os.path.dirname(__file__), u"Collections")
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "flextools.ini")
