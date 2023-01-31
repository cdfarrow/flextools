#
#   RunModule
#
#   A test frame for developing a new Module. 
#   Used by FlexTools\scripts\TestAModule.py 
#

import os
import sys
import imp
# import importlib - TODO: switch to using importlib
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
    # Import the module
    #

    modulePath, moduleName = os.path.split(moduleFolderAndName)
    absPath = os.path.abspath(moduleFolderAndName)
    moduleName, _ = os.path.splitext(moduleName)
    libPath, _ = os.path.split(absPath)

    logger.debug(absPath)

    # Append the local path in case there are local dependencies
    sys.path.append(libPath)

    logger.info(f"Importing {libPath}::{moduleName}")

    try:
        fp, pathname, description = imp.find_module(moduleName, [libPath])
    except ImportError as e:
        logger.error(f"Can't find module '{moduleFolderAndName}'!")
        return None

    try:
        module = imp.load_module(moduleName, fp, pathname, description)
    except FTM_ModuleError as e:
        msg = f"{moduleFolderAndName}:\n{e.message}"
        logger.error(msg)
        return None
    except:
        msg = f"\nException importing module {pathname}\n{traceback.format_exc()}"
        logger.error(msg)
        return None
    finally:
        # Since we may exit via an exception, close fp explicitly.
        if fp:
            fp.close()

    try:
        ftm = module.FlexToolsModule
    except AttributeError:
        logger.error (f"FlexToolsModule object not found in {moduleFolderAndName}.")
        return None
    
    return ftm


#----------------------------------------------------------------

def __RunModule(module, project):

    # --- Import the module ---
    ftm = __ImportModule(module)
    if not ftm:
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
