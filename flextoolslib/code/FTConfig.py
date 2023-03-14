#
#   Project: FlexTools
#   Module:  FTConfig
#
#   Global definitions of data paths and configuration values.
#   
#   Craig Farrow
#   Copyright 2012-2022
#

from os import getcwd, chdir
from os.path import abspath, dirname, join
from sys import argv

from cdfutils.Config import ConfigStore

import logging
logger = logging.getLogger(__name__)

INI_FILENAME = "flextools.ini"

#----------------------------------------------------------- 
# We run from the folder where flextools.ini lives.

# A custom location for flextools.ini can be provided on the command
# line, otherwise we assume the current working directory.

if (argv[-1].endswith(INI_FILENAME)):
    logger.debug(f"Setting CWD: {argv[-1]}")
    INI_PATH = abspath(argv[-1])
    BASE_PATH = dirname(INI_PATH)
    chdir(BASE_PATH)
    argv.pop(-1)
else:
    BASE_PATH = getcwd()

logger.info(f"Current working directory: {BASE_PATH}")

# The default paths are relative to this directory
CONFIG_PATH      = join(BASE_PATH, INI_FILENAME)
MODULES_PATH     = join(BASE_PATH, "Modules")
COLLECTIONS_PATH = join(BASE_PATH, "Collections")

#----------------------------------------------------------- 
# Load the configuration

logger.debug(f"Reading configuration from {CONFIG_PATH}")
FTConfig = ConfigStore(CONFIG_PATH)

# These are included in the configuration file in case users want
# to use a custom location. FlexTrans does this.
if not FTConfig.ModulesPath:
    FTConfig.ModulesPath = MODULES_PATH

if not FTConfig.CollectionsPath:
    FTConfig.CollectionsPath = COLLECTIONS_PATH

