#
#   Project: FlexTools
#   Module:  FTPaths
#
#   Global definitions of data paths for FLExTools
#
#   Craig Farrow
#   Mar 2012
#

from os.path import dirname, join
from sys import argv

import logging
logger = logging.getLogger(__name__)

# We're running from bin\flextools.exe, so jump up a level:
BASE_PATH = dirname(dirname(argv[0]))
logger.info(f"Current working directory: {BASE_PATH}")

# Create absolute paths relative to this directory
CONFIG_PATH      = join(BASE_PATH, "flextools.ini")
MODULES_PATH     = join(BASE_PATH, "Modules")
COLLECTIONS_PATH = join(BASE_PATH, "Collections")

