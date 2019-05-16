
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
import imp
import exceptions
import traceback

import Version
import FTReport
from flexlibs.FLExDBAccess import *
from FTModuleClass import *

# Loads .pth files from Modules\
from FTPaths import MODULES_PATH
import site
site.addsitedir(MODULES_PATH)


# ------------------------------------------------------------------

class ModuleManager (object):

    def __always_import(self, name, path):
        # From Python 2.5 Help section 29.1.1,
        # but skipping the check for the module already being in sys.modules
        # This allows us to have more than one .py Module file with the same
        # name (but in different directories).

        fp, pathname, description = imp.find_module(name, [path])

        try:
            return imp.load_module(name, fp, pathname, description)
        except FTM_ModuleError, e:
            msg = "%s\\%s:\n%s" % (path, name, e.message)
            self.__errors.append(msg)
            return None
        except:
            msg = "Module error: %s\n %s" % (pathname, traceback.format_exc())
            self.__errors.append(msg)
            return None
        finally:
            # Since we may exit via an exception, close fp explicitly.
            if fp:
                fp.close()

    def __openProject(self, dbName, modifyDB):
        #print "__openProject", dbName
        self.db = FLExProject()

        try:
            self.db.OpenProject(dbName,
                                writeEnabled = modifyDB)
        except:
            #print ">>Failed"
            del self.db
            raise
        #print ">>Success"

    def __closeProject(self):
        #print "__closeProject", self.db
        if self.db:
            del self.db     # Free the FDO Cache to get fresh data next time

    def __buildExceptionMessages(self, e, msg):
        __copyMessage = u"Use Ctrl-C to copy this report to the clipboard to see more information."
        eName = details = ""
        # Test for .NET Exception first, since they are also Python Exceptions.
        if isinstance(e, System.Exception): #.NET
            eName = e.GetType().FullName
            details = e.ToString()          # The full stack trace
        elif isinstance(e, exceptions.Exception): #Python
            eName = sys.exc_info()[0].__name__
            eMsg = e.message if hasattr(e, "message") else ""
            eStack = traceback.format_exc()
            details = "{}: {}\n{}".format(eName, eMsg, eStack)

        return " ".join((msg.format(eName), __copyMessage)),\
               details

    # --- Public methods ---

    def LoadAll(self):
        self.db = None
        self.__modules = {}
        self.__errors = []

        libNames = [l for l in os.listdir(MODULES_PATH) \
                       if os.path.isdir(MODULES_PATH + os.sep + l)] \
                   + [""]

        for library in libNames:
            libPath = os.path.join(MODULES_PATH, library)

            modNames = [m[:-3] for m in os.listdir(libPath)
                                        if m.endswith(".py")]
            #print "From library", library, ":", modNames

            for moduleFileName in modNames:
                # Don't try to directly import python files starting with double underscore.
                if moduleFileName.startswith("__"):
                    continue

                # Import named Python module from libPath
                module = self.__always_import(moduleFileName, libPath)

                if not module:
                    print "Warning: FlexToolsModule import failure %s." % moduleFileName
                    continue
                try:
                    ftm = module.FlexToolsModule
                except AttributeError:
                    print "Warning: FlexToolsModule not found in %s." % moduleFileName
                    continue

                if library:
                    moduleFullName = ".".join([library, ftm.GetDocs()[FTM_Name]])
                    modulePath = os.path.join(MODULES_PATH, library, moduleFileName)
                else:
                    moduleFullName = ftm.GetDocs()[FTM_Name]
                    modulePath = os.path.join(MODULES_PATH, moduleFileName)

                if moduleFullName in self.__modules:
                    otherModule = self.__modules[moduleFullName].docs[FTM_Path]
                    errString = "Duplicate module names found in these files (using the first one):\n"\
                                "\t%s \n\t%s" % (otherModule, modulePath)
                    self.__errors.append(errString)
                    continue

                ftm.docs[FTM_Path] = modulePath
                self.__modules[moduleFullName] = ftm

        return self.__errors


    def ListOfNames(self):
        return sorted(self.__modules.keys())

    def GetDocs(self, module_name):
        try:
            return self.__modules[module_name].GetDocs()
        except KeyError:
            return None

    def GetConfigurables(self, module_name):
        try:
            return self.__modules[module_name].GetConfigurables()
        except KeyError:
            return None

    def RunModules(self, dbName, moduleList, reporter, modifyDB = False):
        if not dbName:
            return False

        reporter.Info(u"Opening project %s..." % dbName)
        try:
            self.__openProject(dbName, modifyDB)
        except FDA_ProjectError, e:
            reporter.Error(u"Error opening project: %s"
                           % e.message, e.message)
            return False
        except Exception, e:
            msg, details = self.__buildExceptionMessages(e, "OpenProject failed with exception {}!")
            reporter.Error(msg, details)
            return False

        for moduleName in moduleList:
            if not self.GetDocs(moduleName):
                reporter.Warning("Module %s missing or failed to import." % moduleName)
                continue

            reporter.Blank()
            reporter.Info(u"Running %s (version %s)..." %
                          (moduleName,
                           str(self.__modules[moduleName].docs[FTM_Version])))

            try:
                self.__modules[moduleName].Run(self.db,
                                               reporter,
                                               modify=modifyDB)
            except FDA_RuntimeError, e:
                msg, details = self.__buildExceptionMessages(e, "Module failed with a programming error!")
                reporter.Error(msg, details)
            except Exception, e:
                msg, details = self.__buildExceptionMessages(e, "Module failed with exception {}!")
                reporter.Error(msg, details)
                
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
        print ">>>> Errors <<<<"
        print "\n".join(errList)

    names =  mm.ListOfNames()
    for n in names:
        print ">>>> %s <<<<" % n
        print mm.GetDocs(n)
        print mm.GetConfigurables(n)
        print
