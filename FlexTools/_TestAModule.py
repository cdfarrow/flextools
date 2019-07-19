#
#   _TestAModule
#
#   Test frame for developing a new Module. Run as a command-line application:
#   python _TestAModule <Module> <Project>
#

import os
import sys
import importlib

import logging
logging.basicConfig(
                    stream=sys.stdout,
                    # filename='_TestAModule.log', filemode='w', 
                    level=logging.DEBUG)

logger = logging.getLogger("_TestAModule")

from flexlibs import FLExInit
from flexlibs.FLExProject import (FLExProject, 
    FP_ProjectError, FP_FileNotFoundError)

import FTReport
import FTPaths


#----------------------------------------------------------------

def importModule(moduleFolderAndName):
    #
    # Import the module
    #

    path, moduleName = os.path.split(moduleFolderAndName)
    libPath = os.path.join(FTPaths.MODULES_PATH, path)
    sys.path.append(libPath)

    logger.info("Importing %s::%s" % (libPath, moduleName))

    try:
        module = importlib.import_module(moduleName)

    except ImportError as e:
        logger.error("Can't find module!")
        return None
    except:
        logger.exception("Module error: %s" % moduleName)
        return None

    try:
        ftm = module.FlexToolsModule
    except AttributeError:
        logger.error ("FlexToolsModule not found in %s." \
                      % moduleFolderAndName)
        return None
    
    return ftm

#----------------------------------------------------------------
def usage():
    print ("USAGE: _TestAModule <Module> <Project>")
    sys.exit(1)

#----------------------------------------------------------------

def main():

    # --- Import the module ---

    ftm = importModule(ModuleToTest)
    if not ftm:
        usage()

    logger.info ("Module info:\n%s", ftm.Help())

    # --- Open the project ---
    
    logger.info("Opening project '%s'" % ProjectName)
    FlexDB = FLExProject()

    try:
        FlexDB.OpenProject(projectName = ProjectName)
        logger.info("OK")
    except FP_FileNotFoundError as e:
        logger.error("Project not found! Check the name.")
        return
    except FP_ProjectError as e:
        logger.error("Error opening project!")
        return
        
    # --- Run the module ---
    reporter = FTReport.FTReporter()
    try:
        ftm.Run(FlexDB, reporter)
    except:
        logger.exception("Run() failed:")
        return
    logger.info (repr(reporter.messageCounts))
    for m in reporter.messages:
        logger.info (m)
        

if __name__ == "__main__":

    if len(sys.argv) != 3:
        usage()

    ModuleToTest = sys.argv[1] 
    ProjectName  = sys.argv[2] 

    FLExInit.Initialize()

    main()

    FLExInit.Cleanup()
