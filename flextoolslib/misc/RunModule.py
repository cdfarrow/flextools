#
#   RunModule
#
#   A test frame for developing a new Module. 
#   Used by FlexTools\scripts\TestAModule.py 
#

import os
import sys
import importlib

import traceback

import logging
logger = logging.getLogger(__name__)

from flexlibs import FLExInitialize, FLExCleanup
from flexlibs import (
    FLExProject,
    FP_ProjectError, 
    FP_FileNotFoundError)

from ..code.FTModuleClass import FTM_ModuleError
from ..code.FTReport import FTReporter

    
#----------------------------------------------------------------

def __ImportModule(moduleFolderAndName):
    #
    # Import the module given the full path and file name.
    #

    modulePath = os.path.abspath(moduleFolderAndName)
    moduleName = os.path.split(moduleFolderAndName)[1]
    moduleName = os.path.splitext(moduleName)[0]
  
    libPath = os.path.split(modulePath)[0]

    # Append the local path in case there are local dependencies
    sys.path.append(libPath)

    logger.info(f"Importing {libPath}::{moduleName}")

    # Manually import the Python module.
    # moduleName is the name of the module in Python namespace.
    # modulePath is the full path+filename of the module.

    spec = importlib.util.spec_from_file_location(moduleName, modulePath)
    if spec is None:
        logger.error(f"{modulePath} not found.")
        return None
        
    logger.debug(f"Attempting import of {modulePath}")
    try:
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    except FTM_ModuleError as e:
        msg = f"{modulePath}:\n{e.message}"
    except:
        msg = f"Module error: {modulePath}\n {traceback.format_exc()}"
        
    if msg:
        logger.error(msg)
    return None


#----------------------------------------------------------------

def __RunModule(module, project):

    # --- Import the module ---
    mod = __ImportModule(module)
    
    if not mod:
        return False

    try:
        ftm = mod.FlexToolsModule
    except AttributeError:
        logger.warning(f"Warning: FlexToolsModule not found in {module}")
        return False

    logger.info (f"Module info:\n{ftm.Help()}")

    # --- Open the project ---
    logger.info(f"Opening project '{project}'")
    FlexDB = FLExProject()

    try:
        FlexDB.OpenProject(projectName = project)
        logger.info("OK")
    except FP_FileNotFoundError as e:
        logger.error(f"Project '{project}' not found!")
        return False
    except FP_ProjectError as e:
        logger.error(f"Error opening project!\n{e.message}")
        return False
        
    # --- Run the module ---
    reporter = FTReporter()
    try:
        ftm.Run(FlexDB, reporter)
    except:
        logger.exception("Runtime error:")
        return False
    
    TYPE_LOOKUP = ["INFO", "WARN", "ERR ", "    "]
    for m in reporter.messages:
        msgType, msg, ref = m
        logger.info (f"{TYPE_LOOKUP[msgType]}: {msg}")
        if ref:
            logger.info (f">>>>  {ref}")
    
    FlexDB.CloseProject()
    
    return True
    
    
def RunModule(module, project):

    FLExInitialize()

    result = __RunModule(module, project)
    
    FLExCleanup()
    
    return result
