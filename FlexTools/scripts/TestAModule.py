#
#   _TestAModule
#
#   Test frame for developing a new Module. Run as a command-line application:
#   python _TestAModule <Module> <Project>
#

import os
import sys
import imp
# import importlib - TODO: switch to using importlib
import traceback

import logging
logging.basicConfig(
                    stream=sys.stdout,
                    # filename='_TestAModule.log', filemode='w', 
                    level=logging.DEBUG)

logger = logging.getLogger("_TestAModule")

from flexlibs import FLExInitialize, FLExCleanup
from flexlibs import (
    FLExProject, 
    FP_ProjectError, 
    FP_FileNotFoundError)

from FTModuleClass import FTM_ModuleError
import FTReport
import FTPaths


#----------------------------------------------------------------

def importModule(moduleFolderAndName):
    #
    # Import the module
    #

    path, moduleName = os.path.split(moduleFolderAndName)
    moduleName, ext = os.path.splitext(moduleName)
    libPath = os.path.join(FTPaths.MODULES_PATH, path)
    absPath = os.path.abspath(os.path.join(FTPaths.MODULES_PATH,        
                                            moduleFolderAndName))
    logger.debug(absPath)

    # Append the local path in case there are local dependencies
    sys.path.append(libPath)

    logger.info("Importing %s::%s" % (libPath, moduleName))

    try:
        fp, pathname, description = imp.find_module(moduleName, [libPath])
    except ImportError as e:
        logger.error("Can't find module '%s!'" % moduleFolderAndName)
        return None

    try:
        module = imp.load_module(moduleName, fp, pathname, description)
    except FTM_ModuleError as e:
        msg = "%s\\%s:\n%s" % (path, moduleName, e.message)
        logger.error(msg)
        return None
    except:
        msg = "Module error: %s\n %s" % (pathname, traceback.format_exc())
        logger.error(msg)
        return None
    finally:
        # Since we may exit via an exception, close fp explicitly.
        if fp:
            fp.close()

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


#----------------------------------------------------------------

def main(module, project):

    # --- Import the module ---
    ftm = importModule(module)
    if not ftm:
        usage()
        return

    logger.info ("Module info:\n%s", ftm.Help())

    # --- Open the project ---
    logger.info("Opening project '%s'" % project)
    FlexDB = FLExProject()

    try:
        FlexDB.OpenProject(projectName = project)
        logger.info("OK")
    except FP_FileNotFoundError as e:
        logger.error("Project '%s' not found!" % project)
        return
    except FP_ProjectError as e:
        logger.error("Error opening project!")
        return
        
    # --- Run the module ---
    reporter = FTReport.FTReporter()
    try:
        ftm.Run(FlexDB, reporter)
    except:
        logger.exception("Runtime error:")
        return
    
    rLOOKUP = ["INFO", "WARN", "ERR ", "    "]
    for m in reporter.messages:
        t, msg, extra = m
        logger.info ("%s: %s" % (rLOOKUP[t], msg))
        if extra:
            logger.info (">>>>  %s" % extra)
    
    FlexDB.CloseProject()
    

if __name__ == "__main__":

    if len(sys.argv) != 3:
        usage()
        sys.exit(1)

        
    ModuleToTest = sys.argv[1]
    ProjectName  = sys.argv[2]

    FLExInitialize()

    main(ModuleToTest, ProjectName)

    FLExCleanup()
