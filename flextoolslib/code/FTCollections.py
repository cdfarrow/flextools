#
#   Project: FlexTools
#   Module:  FTCollections
#
#   Manages user-defined collections of modules.
#    - Loads and saves configuration from disk.
#    - Provides an interface for UI manipulation of collections.
#
#   Craig Farrow
#   2009-2023
#

import os

from configparser import ConfigParser, NoOptionError

from .FTConfig import FTConfig
COLLECTIONS_PATH = FTConfig.CollectionsPath

import logging
logger = logging.getLogger(__name__)


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
    
        def __sortedModulesList(cp):
            # This function bridges between the old style ini file, where
            # an _Order option was used to specify the order of the modules.
            # If _Order doesn't exist, then it is the new style.
            # DELETE THIS SPECIAL HANDLING AFTER DEC2023 GIVING TIME FOR 
            # USERS' INI FILES TO BE UPDATED TO THE NEW FORMAT.
            # ALSO, ONLY CALL WriteAll() IF CHANGES ARE MADE.
            
            try:
                mods = [(cp.getint(m, self.ORDER_OPTION), m) for m in cp.sections()]
            except NoOptionError:
                return cp.sections()
                
            # Sort the modules according to the _Order option value. 
            # This handles cases where there are gaps in the sequence 
            # (such as when the FlexTrans installer removes the Settings
            # module from users' Tools.ini file).
            sortedModules = [m for i, m in sorted(mods)]
            return sortedModules
               
         
        # Load all the collection info

        collectionNames = [f for f in os.listdir(COLLECTIONS_PATH)
                                    if f.endswith(self.COLLECTIONS_SUFFIX)]

        self.collections = {}

        for collectionName in collectionNames:
            cp = ConfigParser(interpolation=None)
            if cp.read(os.path.join(COLLECTIONS_PATH, collectionName)):
                modules = __sortedModulesList(cp)
                # Strip '.ini' for the collection name
                self.collections[collectionName[:-4]] = modules
            else:
                logger.warning(f"CollectionsManager init: Failed to read {collectionName}")

    # ---- Access ----

    def Names(self):
        return (list(self.collections.keys()))

    def ListOfModules(self, collectionName):
        if collectionName not in self.collections:
            raise FTC_NameError(f"Bad collection name '{collectionName}'")
        return self.collections[collectionName]

    # ---- Creating and Modifying ----

    def Add(self, collectionName):
        if collectionName in self.collections:
            raise FTC_ExistsError(collectionName + " already exists.")
        self.collections[collectionName] = []
        self.WriteOne(collectionName, [])

    def Delete(self, collectionName):
        if collectionName not in self.collections:
            raise FTC_NameError("Collection not found.")
            
        try:
            os.remove(os.path.join(COLLECTIONS_PATH,
                                   collectionName + self.COLLECTIONS_SUFFIX))
        except:
            pass
        self.collections.pop(collectionName)

    def Rename(self, collectionName, newName):
        if collectionName not in self.collections:
            raise FTC_NameError("Collection not found.")
        if newName.lower() in [c.lower() for c in self.collections]:
            raise FTC_ExistsError(f"'{newName}' already exists.")

        try:
            os.rename(os.path.join(COLLECTIONS_PATH,
                                   collectionName + self.COLLECTIONS_SUFFIX),
                      os.path.join(COLLECTIONS_PATH,
                                   newName + self.COLLECTIONS_SUFFIX))
        except:
            raise FTC_BadNameError("An error occured renaming the collection. The name must be a valid filename.")
        else:
            self.collections[newName] = self.collections.pop(collectionName)

    def AddModule(self, collectionName, moduleName):
        modules = self.collections[collectionName]
        if moduleName in modules:
            raise FTC_ExistsError(moduleName + " already exists.")
        modules.append(moduleName)

    def RemoveModule(self, collectionName, moduleName):
        modules = self.collections[collectionName]
        try:
            modules.remove(moduleName)
        except ValueError:
            pass

    def MoveModuleUp(self, collectionName, moduleName):
        modules = self.collections[collectionName]
        i = modules.index(moduleName)
        if i > 0:
            modules.insert(i - 1, modules.pop(i))

    def MoveModuleDown(self, collectionName, moduleName):
        modules = self.collections[collectionName]
        i = modules.index(moduleName)
        if i < len(modules) - 1:
            modules.insert(i + 1, modules.pop(i))

    # ---------

    def WriteAll(self):
        for (name, modules) in self.collections.items():
            self.WriteOne(name, modules)

    def WriteOne(self, name, modules):
        # Create an empty section for each module. ConfigParser preserves 
        # the order.
        cp = ConfigParser(interpolation=None)
        cp.read_dict({m : {} for m in modules})
            
        with open(os.path.join(COLLECTIONS_PATH,
                               name + self.COLLECTIONS_SUFFIX), 'w') as f:
            cp.write(f)
  
