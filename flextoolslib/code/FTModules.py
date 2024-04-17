#
#   Project: FlexTools
#   Module:  FTModules
#
#   Class that loads and wraps FlexTools Modules.
#
#   Craig Farrow
#   Apr 2009
#
#   Attempts to load all *.py files in the Modules directory (including
#   subdirectories). These all need to conform to the specification for
#   FlexTools modules -- See FTModuleClass.py
#
#

import os
import sys
import importlib.util
import traceback

import System

from . import FTReport
from flexlibs import (
    FLExProject, 
    FP_ProjectError, 
    FP_RuntimeError,
    )

from .FTModuleClass import *

# Loads .pth files from Modules\
from .FTConfig import FTConfig
MODULES_PATH = FTConfig.ModulesPath

import site
site.addsitedir(MODULES_PATH)


import logging
logger = logging.getLogger(__name__)

# ------------------------------------------------------------------

class ModuleManager (object):

    def __importModule(self, moduleName, modulePath):
        # Manually import the Python module.
        # moduleName is the name of the module in Python namespace.
        # modulePath is the full path+filename of the module.

        spec = importlib.util.spec_from_file_location(moduleName, modulePath)
        if spec is None:
            self.__errors.append(f"{modulePath} not found.")
            return None
            
        logger.debug(f"Attempting import of {modulePath}")
        try:
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod
        except FTM_ModuleError as e:
            msg = f"{modulePath}:\n{e.message}"
            self.__errors.append(msg)
            return None
        except:
            msg = f"Module error: {modulePath}\n {traceback.format_exc()}"
            self.__errors.append(msg)
            return None

    def __openProject(self, projectName, modifyAllowed):
        #logger.debug("__openProject %s" % projectName)
        self.project = FLExProject()

        try:
            self.project.OpenProject(projectName,
                                     writeEnabled = modifyAllowed)
        except:
            logger.error("Project failed to open: %s" % projectName)
            del self.project
            raise
        logger.info("Project opened: %s" % projectName)

    def __closeProject(self):
        #logger.debug("__closeProject %s" % repr(self.project))
        if self.project:
            # Save any changes and release the LCM Cache.
            self.project.CloseProject()
            del self.project

    def __buildExceptionMessages(self, e, msg):
        __copyMessage = "Use Ctrl-C to copy this report to the clipboard to see more information."
        eName = details = ""
        # Test for .NET Exception first, since they are also Python Exceptions.
        if isinstance(e, System.Exception): #.NET
            eName = e.GetType().FullName
            details = e.ToString()          # The full stack trace
        elif isinstance(e, Exception):      #Python
            eName = sys.exc_info()[0].__name__
            eMsg = e.message if hasattr(e, "message") else ""
            eStack = traceback.format_exc()
            details = "{}: {}\n{}".format(eName, eMsg, eStack)

        return " ".join((msg.format(eName), __copyMessage)),\
               details

    # --- Public methods ---

    def LoadAll(self):
        # Loads all the FlexTools modules from the Modules folder.
        # Returns a list of error messages about duplicate module names.
        # An empty list means there were no errors.
        
        self.project = None
        self.__modules = {}
        self.__errors = []

        libNames = [l for l in os.listdir(MODULES_PATH) \
                       if os.path.isdir(os.path.join(MODULES_PATH,l))] \
                   + [""]

        try:
            libNames.remove("__pycache__")
        except ValueError:
            pass
        
        logger.info("Module libraries found: %s" % libNames)
        
        for library in libNames:
            libPath = os.path.join(MODULES_PATH, library)

            modNames = [m for m in os.listdir(libPath)
                            if m.endswith(".py")]
            logger.info("From library '%s': %s" % (library, repr(modNames)))

            for moduleFileName in modNames:
                # Don't try to directly import python files starting with
                # double underscore.
                if moduleFileName.startswith("__"):
                    continue

                moduleFullPath = os.path.join(libPath, moduleFileName)
                moduleName = os.path.splitext(moduleFileName)[0]
                
                # Import the Python module
                module = self.__importModule(moduleName, moduleFullPath)

                if not module:
                    logger.warning(f"Warning: FlexToolsModule import failure - {moduleFullPath}")
                    continue

                try:
                    ftm = module.FlexToolsModule
                except AttributeError:
                    logger.warning(f"Warning: FlexToolsModule not found in {moduleFullPath}")
                    continue

                if library:
                    moduleFullName = ".".join([library, ftm.GetDocs()[FTM_Name]])
                else:
                    moduleFullName = ftm.GetDocs()[FTM_Name]

                if moduleFullName in self.__modules:
                    otherModule = self.__modules[moduleFullName].docs[FTM_Path]
                    errString = "Duplicate module names found in these files (using the first one):\n"\
                                "\t%s \n\t%s" % (otherModule, moduleFullPath)
                    self.__errors.append(errString)
                    continue

                ftm.docs[FTM_Path] = moduleFullPath
                self.__modules[moduleFullName] = ftm

        return self.__errors


    def ListOfNames(self):
        return sorted(self.__modules.keys())

    def GetDocs(self, module_name):
        try:
            return self.__modules[module_name].GetDocs()
        except KeyError:
            return None
            
    def CanModify(self, module_name):
        docs = self.GetDocs(module_name)
        return docs[FTM_ModifiesDB] if docs else False

    def GetConfigurables(self, module_name):
        try:
            return self.__modules[module_name].GetConfigurables()
        except KeyError:
            return None

    def RunModules(self, projectName, moduleList, reporter, modifyAllowed = False):
        if not projectName:
            return False

        reporter.Info("Opening project %s..." % projectName)
        try:
            self.__openProject(projectName, modifyAllowed)
        except FP_ProjectError as e:
            logger.error(e.message)
            reporter.Error("Error opening project: %s"
                           % e.message, e.message)
            return False
        except Exception as e:
            msg, details = self.__buildExceptionMessages(e, "OpenProject failed with exception {}!")
            logger.error(details)
            reporter.Error(msg, details)
            return False

        for moduleName in moduleList:
            docs = self.GetDocs(moduleName)
            if not docs:
                reporter.Warning("Module %s missing or failed to import." % moduleName)
                continue

            reporter.Blank()

            # Issue #20 - only display the base name of the module 
            # in the main UI.
            try:
                displayName = moduleName.split(".", 1)[1]
            except IndexError:
                # It is a top-level module with no '<library>.' prefix.
                displayName = moduleName

            reporter.Info("Running %s (version %s)..." %
                          (displayName,
                           str(docs[FTM_Version])))
            
            # In simplified mode, we always allow mods if the module does.
            if FTConfig.simplifiedRunOps:
                modifyAllowed = docs[FTM_ModifiesDB]

            try:
                self.__modules[moduleName].Run(self.project,
                                               reporter,
                                               modifyAllowed=modifyAllowed)
            except FP_RuntimeError as e:
                msg, details = self.__buildExceptionMessages(e, "Module failed with a programming error!")
                reporter.Error(msg, details)
            except Exception as e:
                msg, details = self.__buildExceptionMessages(e, "Module failed with exception {}!")
                reporter.Error(msg, details)
                
            if FTConfig.stopOnError:
                if reporter.messageCounts[reporter.ERROR]:
                    break

        numErrors   = reporter.messageCounts[reporter.ERROR]
        numWarnings = reporter.messageCounts[reporter.WARNING]
        reporter.Info("Processing completed with %d error%s and %d warning%s" \
                      % (numErrors,   "" if numErrors==1 else "s",
                         numWarnings, "" if numWarnings==1 else "s"))
        self.__closeProject()

        return True


# ------------------------------------------------------------------

if __name__ == '__main__':
    mm = ModuleManager()
    errList = mm.LoadAll()
    if errList:
        print(">>>> Errors <<<<")
        print("\n".join(errList))

    names =  mm.ListOfNames()
    for n in names:
        print(">>>> %s <<<<" % n)
        print(mm.GetDocs(n))
        print(mm.GetConfigurables(n))
        print()
