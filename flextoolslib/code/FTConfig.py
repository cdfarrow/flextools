#
#   Project: FlexTools
#   Module:  FTConfig
#
#   Global definitions of data paths and configuration values.
#   
#   Craig Farrow
#   Copyright 2012-2022
#

from os import getcwd
from os.path import dirname, join
from sys import argv

from cdfutils.Config import ConfigStore

import logging
logger = logging.getLogger(__name__)

#----------------------------------------------------------- 
# We're running from the folder where flextools.ini lives:
BASE_PATH = getcwd()
logger.info(f"Current working directory: {BASE_PATH}")

# The default paths are relative to this directory
CONFIG_PATH      = join(BASE_PATH, "flextools.ini")
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

