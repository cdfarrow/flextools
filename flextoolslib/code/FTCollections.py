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

from configparser import (
    ConfigParser,
    DEFAULTSECT,
    NoOptionError,
    MissingSectionHeaderError,
    )

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
class CollectionsInfo(list):
    """
    A wrapper class for the collections list of modules, with an extra
    property, "disableRunAll".
    """
    def __init__(self, iterable):
        list.__init__(self, iterable)
        self.disableRunAll = False

# ---------------------------------------------------------------------
class CollectionsManager(object):

    ORDER_OPTION = "_Order"
    DISABLERUNALL = "DisableRunAll"
    COLLECTIONS_SUFFIX = ".ini"

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
                return CollectionsInfo(cp.sections())
                
            # Sort the modules according to the _Order option value. 
            # This handles cases where there are gaps in the sequence 
            # (such as when the FlexTrans installer removes the Settings
            # module from users' Tools.ini file).
            sortedModules = CollectionsInfo(m for i, m in sorted(mods))
            return sortedModules
               
         
        # Load all the collection info

        collectionNames = [f for f in os.listdir(COLLECTIONS_PATH)
                                    if f.endswith(self.COLLECTIONS_SUFFIX)]

        self.collections = {}

        for collectionName in collectionNames:
            cp = ConfigParser(interpolation=None)
            try:
                result = cp.read(os.path.join(COLLECTIONS_PATH, collectionName))
            except MissingSectionHeaderError:
                logger.warning(f"CollectionsManager init: Missing DEFAULT section in {collectionName}")
                continue
            if result:
                collectionsInfo = __sortedModulesList(cp)
                if cp.has_option(DEFAULTSECT, self.DISABLERUNALL):
                    collectionsInfo.disableRunAll = True

                # Strip '.ini' for the collection name
                name = os.path.splitext(collectionName)[0]
                self.collections[name] = collectionsInfo
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
        newCollection = CollectionsInfo()
        self.collections[collectionName] = newCollection
        self.WriteOne(collectionName, newCollection)

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
            
        # Prevent duplicate names, but allow change of case
        if newName.lower() != collectionName.lower():
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
        collectionsInfo = self.collections[collectionName]
        if moduleName in collectionsInfo:
            raise FTC_ExistsError(moduleName + " already exists.")
        collectionsInfo.append(moduleName)

    def RemoveModule(self, collectionName, moduleName):
        collectionsInfo = self.collections[collectionName]
        try:
            collectionsInfo.remove(moduleName)
        except ValueError:
            pass

    def MoveModuleUp(self, collectionName, moduleName):
        collectionsInfo = self.collections[collectionName]
        i = collectionsInfo.index(moduleName)
        if i > 0:
            collectionsInfo.insert(i - 1, collectionsInfo.pop(i))

    def MoveModuleDown(self, collectionName, moduleName):
        collectionsInfo = self.collections[collectionName]
        i = collectionsInfo.index(moduleName)
        if i < len(collectionsInfo) - 1:
            collectionsInfo.insert(i + 1, collectionsInfo.pop(i))

    # ---------

    def WriteAll(self):
        for (name, collectionsInfo) in self.collections.items():
            self.WriteOne(name, collectionsInfo)

    def WriteOne(self, name, collectionsInfo):
        # Create an empty section for each module. ConfigParser preserves 
        # the order.
        cp = ConfigParser(interpolation=None)
        cp.read_dict({m : {} for m in collectionsInfo})

        if collectionsInfo.disableRunAll:
            cp[DEFAULTSECT][self.DISABLERUNALL] = repr(True)
            
        with open(os.path.join(COLLECTIONS_PATH,
                               name + self.COLLECTIONS_SUFFIX), 'w') as f:
            cp.write(f)
