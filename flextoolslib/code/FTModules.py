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
    FP_FileLockedError,
    FP_MigrationRequired,
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
        __copyMessage = _("Use Ctrl-C to copy this report to the clipboard to see more information.")
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
        
        logger.info(f"Module libraries found: {libNames}")
        
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
                    errLines = [
                        _("Duplicate module names found in these files (using the first one):"),
                        "\t{}".format(otherModule),
                        "\t{}".format(moduleFullPath)]
                    errString = "\n".join(errLines)
                    self.__errors.append(errString)
                    continue

                ftm.docs[FTM_Path] = moduleFullPath
                self.__modules[moduleFullName] = ftm

        return self.__errors

    # NameToPath() and PathToName() are used by FTCollections to map 
    # between module display names (used throughout FlexTools for 
    # referencing modules) and relative pathnames (saved in the 
    # Collections ini files).
    # If the lookup fails, then the passed-in value is returned. This
    # allows the display name to act as a fallback when the file can't 
    # be found/loaded. 

    def NameToPath(self, moduleName):
        docs = self.GetDocs(moduleName)
        if docs:
            return os.path.relpath(docs[FTM_Path], MODULES_PATH)
        return moduleName

    def PathToName(self, pathOrName):
        for name, module in self.__modules.items():
            if module.GetDocs()[FTM_Path].endswith(pathOrName):
                return name
        return pathOrName

    def ListOfNames(self):
        return sorted(self.__modules.keys())

    def GetDocs(self, moduleName):
        try:
            return self.__modules[moduleName].GetDocs()
        except KeyError:
            return None

    def CanModify(self, moduleName):
        docs = self.GetDocs(moduleName)
        return docs[FTM_ModifiesDB] if docs else False

    def GetConfigurables(self, moduleName):
        try:
            return self.__modules[moduleName].GetConfigurables()
        except KeyError:
            return None

    def RunModules(self, projectName, moduleList, reporter, modifyAllowed = False):
        if not projectName:
            return False

        reporter.Info(_("Opening project '{}'...").format(projectName))
        try:
            self.__openProject(projectName, modifyAllowed)
        except FP_FileLockedError as e:
            logger.error(e.message)
            reporter.Error(_("Error opening project:") +\
                _("This project is in use by another program. To allow shared access to this project, turn on the sharing option in the Sharing tab of the Fieldworks Project Properties dialog."))
            return False
        except FP_MigrationRequired as e:
            logger.error(e.message)
            reporter.Error(_("Error opening project:") +\
                           _("This project needs to be opened in FieldWorks in order for it to be migrated to the latest format."))
            return False
        except FP_ProjectError as e:
            logger.error(e.message)
            reporter.Error(_("Error opening project:") + e.message,
                           e.message)
            return False
        except Exception as e:
            msg, details = self.__buildExceptionMessages(e, _("OpenProject failed with exception {}!"))
            logger.error(msg)
            logger.error(details)
            reporter.Error(msg, details)
            return False

        for moduleName in moduleList:
            docs = self.GetDocs(moduleName)
            if not docs:
                reporter.Error(_("Module '{}' is missing or failed to import.").format(moduleName))
                continue

            reporter.Blank()

            # Issue #20 - only display the base name of the module 
            # in the main UI.
            try:
                displayName = moduleName.split(".", 1)[1]
            except IndexError:
                # It is a top-level module with no '<library>.' prefix.
                displayName = moduleName

            reporter.Info(_("Running '{}' (version {})...").format(
                           displayName,
                           str(docs[FTM_Version])))
            
            # In simplified mode, we always allow mods if the module does.
            if FTConfig.simplifiedRunOps:
                modifyAllowed = docs[FTM_ModifiesDB]

            try:
                self.__modules[moduleName].Run(self.project,
                                               reporter,
                                               modifyAllowed=modifyAllowed)
            except FP_RuntimeError as e:
                msg, details = self.__buildExceptionMessages(e, _("Module failed with a programming error!"))
                logger.error(msg)
                logger.error(details)
                reporter.Error(msg, details)
            except Exception as e:
                msg, details = self.__buildExceptionMessages(e, _("Module failed with exception {}!"))
                logger.error(msg)
                logger.error(details)
                reporter.Error(msg, details)
                
            if FTConfig.stopOnError:
                if reporter.messageCounts[reporter.ERROR]:
                    break

        numErrors   = reporter.messageCounts[reporter.ERROR]
        numWarnings = reporter.messageCounts[reporter.WARNING]
        reporter.Info(_("Processing completed. Errors: {}; Warnings: {}").format(
                        numErrors, numWarnings))
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
