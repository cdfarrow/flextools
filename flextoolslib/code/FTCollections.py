
#
#   Project: FlexTools
#   Module:  FTCollections
#
#   Manages user-defined collections of modules.
#    - Loads and saves configuration from disk.
#    - Provides interface for UI manipulation of collections.
#
#   Craig Farrow
#   Oct 2009
#   v0.01
#

from __future__ import unicode_literals
from builtins import str

import os

from configparser import ConfigParser

from FTPaths import COLLECTIONS_PATH

# ---- Exceptions ----

class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class FTC_NameError(Error):
    """
    Exception raised for looking up a collection name that doesn't exist.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message

class FTC_ExistsError(Error):
    """
    Exception raised for adding or renaming to a collection name
    that is already in use.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message

class FTC_BadNameError(Error):
    """
    Exception raised for a name that isn't valid.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message
# ---------------------------------------------------------------------
class CollectionsManager(object):

    ORDER_OPTION = "_Order"
    COLLECTIONS_SUFFIX = ".ini"
    assert(len(COLLECTIONS_SUFFIX) == 4)

    def __init__(self):
        # Load all the collection info

        # If the path to os.listdir is unicode, then the file names will
        # be correctly decoded and returned as unicode.
        collectionNames = [f for f in os.listdir(COLLECTIONS_PATH)
                                    if f.endswith(self.COLLECTIONS_SUFFIX)]

        self.collectionsConfig = {}

        for collectionName in collectionNames:
            cp = ConfigParser(interpolation=None)
            if cp.read(os.path.join(COLLECTIONS_PATH, collectionName)):
                self.collectionsConfig[collectionName[:-4]] = cp # Strip '.ini'
            else:
                print("Failed to read", collectionName)

    # ---- Access ----

    def Names(self):
        return (list(self.collectionsConfig.keys()))

    def ListOfModules(self, collectionName):
        if collectionName not in self.collectionsConfig:
            raise FTC_NameError("Bad collection name '%s'" % collectionName)
        cp = self.collectionsConfig[collectionName]
        modules = cp.sections()
        sortedModules = [0] * len(modules)
        for moduleName in modules:
            try:
                order = cp.getint(moduleName, self.ORDER_OPTION)
            except:
                # Error in collections file; skip this entry
                continue
            sortedModules[order-1] = moduleName
        return (sortedModules)

    def ModuleConfiguration(self, collectionName, moduleName):
        return (self.collectionsConfig[collectionName].options(moduleName))

    # ---- Creating and Modifying ----

    def Add(self, collectionName):
        if collectionName in self.collectionsConfig:
            raise FTC_ExistsError(collectionName + " already exists.")
        cp = ConfigParser(interpolation=None)
        self.collectionsConfig[collectionName] = cp
        self.WriteOne(collectionName, cp)
        return

    def Delete(self, collectionName):
        if collectionName not in self.collectionsConfig:
            raise FTC_NameError("Collection not found.")
        try:
            os.remove(os.path.join(COLLECTIONS_PATH,
                                   collectionName + self.COLLECTIONS_SUFFIX))
        except:
            pass
        del(self.collectionsConfig[collectionName])
        return

    def Rename(self, collectionName, newName):
        if collectionName not in self.collectionsConfig:
            raise FTC_NameError("Collection not found.")
        if newName in self.collectionsConfig:
            raise FTC_ExistsError("'" + newName + "' already exists.")

        try:
            os.rename(os.path.join(COLLECTIONS_PATH,
                                   collectionName + self.COLLECTIONS_SUFFIX),
                      os.path.join(COLLECTIONS_PATH,
                                   newName + self.COLLECTIONS_SUFFIX))
        except:
            raise FTC_BadNameError("Error occured renaming collection file. Check that the name is a valid file name.")
        else:
            self.collectionsConfig[newName] = self.collectionsConfig.pop(collectionName)


    def AddModule(self, collectionName, moduleName, configuration=[]):
        cp = self.collectionsConfig[collectionName]
        if cp.has_section(moduleName):
            raise FTC_ExistsError(moduleName + " already exists.")
        cp.add_section(moduleName)
        cp.set(moduleName, self.ORDER_OPTION, str(len(cp.sections())))
        for configItem in configuration:
            cp.set(moduleName, configItem.Name, configItem.Default)
        return

    def RemoveModule(self, collectionName, moduleName):
        cp = self.collectionsConfig[collectionName]
        order = cp.getint(moduleName, self.ORDER_OPTION)
        cp.remove_section(moduleName)
        for m in cp.sections():
            this_order = cp.getint(m, self.ORDER_OPTION)
            if  this_order > order:
                cp.set(m, self.ORDER_OPTION, str(this_order - 1))

    def MoveModuleUp(self, collectionName, moduleName):
        cp = self.collectionsConfig[collectionName]
        order = cp.getint(moduleName, self.ORDER_OPTION)
        if order > 1:
            for m in cp.sections():
                this_order = cp.getint(m, self.ORDER_OPTION)
                if this_order == order - 1:
                    cp.set(m, self.ORDER_OPTION, str(order))
            cp.set(moduleName, self.ORDER_OPTION, str(order - 1))

    def MoveModuleDown(self, collectionName, moduleName):
        cp = self.collectionsConfig[collectionName]
        order = cp.getint(moduleName, self.ORDER_OPTION)
        if order < len(cp.sections()):
            for m in cp.sections():
                this_order = cp.getint(m, self.ORDER_OPTION)
                if this_order == order + 1:
                    cp.set(m, self.ORDER_OPTION, str(order))
            cp.set(moduleName, self.ORDER_OPTION, str(order + 1))

    # ---------

    def WriteAll(self):
        for (name, cp) in self.collectionsConfig.items():
            self.WriteOne(name, cp)

    def WriteOne(self, name, cp):
        #print "Writing:", name, cp.sections()
        f = open(os.path.join(COLLECTIONS_PATH,
                              name + self.COLLECTIONS_SUFFIX), "w")
        cp.write(f)
        f.close()
