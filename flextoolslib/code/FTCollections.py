#
#   Project: FlexTools
#   Module:  FTCollections
#
#   Manages user-defined collections of modules.
#    - Loads and saves configuration from disk.
#    - Provides functions for manipulation of collections for use by
#      UICollections.py.
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
class Collection(list):
    """
    A wrapper class for the collections list of modules, with an extra
    property, "disableRunAll".
    """
    def __init__(self, *args):
        list.__init__(self, *args)
        self.disableRunAll = False

# ---------------------------------------------------------------------
class CollectionsManager(object):

    ORDER_OPTION = "_Order"
    DISABLERUNALL = "DisableRunAll"
    COLLECTIONS_SUFFIX = ".ini"

    def __init__(self, moduleManager):

        # moduleManager provides mapping functions between module display 
        # names and pathnames. We store the latter in the collections ini 
        # file (for language independence). However, if the file can't be 
        # found/loaded, then we save the module name. 
        # (Aug2025: Changed to use pathname in the ini file for 
        # multi-lingual support.)
        self.mm = moduleManager
        
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
                modules = cp.sections()
                converted = [self.mm.PathToName(p) for p in modules]
                collection = Collection(converted)
                if cp.has_option(DEFAULTSECT, self.DISABLERUNALL):
                    collection.disableRunAll = True

                # Strip '.ini' for the collection name
                name = os.path.splitext(collectionName)[0]
                self.collections[name] = collection
            else:
                logger.warning(f"CollectionsManager init: Failed to read {collectionName}")

    # ---- Access ----

    def Names(self):
        return (list(self.collections.keys()))

    def ListOfModules(self, collectionName):
        if collectionName not in self.collections:
            # Obscure scenario: don't translate
            raise FTC_NameError(f"Bad collection name '{collectionName}'")
        return self.collections[collectionName]

    # ---- Creating and Modifying ----

    def Add(self, collectionName):
        if collectionName in self.collections:
            # NOTE: Parameter = collection name
            raise FTC_ExistsError(_("'{}' already exists.").format(collectionName))
        newCollection = Collection()
        self.collections[collectionName] = newCollection
        self.WriteOne(collectionName, newCollection)

    def Delete(self, collectionName):
        if collectionName not in self.collections:
            # Obscure scenario: don't translate
            raise FTC_NameError(f"Collection not found '{collectionName}'")
            
        try:
            os.remove(os.path.join(COLLECTIONS_PATH,
                                   collectionName + self.COLLECTIONS_SUFFIX))
        except:
            pass
        self.collections.pop(collectionName)

    def Rename(self, collectionName, newName):
        if collectionName not in self.collections:
            # Obscure scenario: don't translate
            raise FTC_NameError(f"Collection not found '{collectionName}'")
            
        # Prevent duplicate names, but allow change of case
        if newName.lower() != collectionName.lower():
            if newName.lower() in [c.lower() for c in self.collections]:
                # NOTE: Parameter = collection name
                raise FTC_ExistsError(_("'{}' already exists.").format(newName))

        try:
            os.rename(os.path.join(COLLECTIONS_PATH,
                                   collectionName + self.COLLECTIONS_SUFFIX),
                      os.path.join(COLLECTIONS_PATH,
                                   newName + self.COLLECTIONS_SUFFIX))
        except:
            # Obscure scenario: don't translate
            raise FTC_BadNameError("An error occured renaming the collection. The name must be a valid filename.")
        else:
            self.collections[newName] = self.collections.pop(collectionName)

    def AddModule(self, collectionName, moduleName):
        collection = self.collections[collectionName]
        if moduleName in collection:
            # NOTE: Parameter = module name
            raise FTC_ExistsError(_("'{}' is already in the collection.").format(moduleName))
        collection.append(moduleName)

    def RemoveModule(self, collectionName, moduleName):
        collection = self.collections[collectionName]
        try:
            collection.remove(moduleName)
        except ValueError:
            pass

    def MoveModuleUp(self, collectionName, moduleName):
        collection = self.collections[collectionName]
        i = collection.index(moduleName)
        if i > 0:
            collection.insert(i - 1, collection.pop(i))

    def MoveModuleDown(self, collectionName, moduleName):
        collection = self.collections[collectionName]
        i = collection.index(moduleName)
        if i < len(collection) - 1:
            collection.insert(i + 1, collection.pop(i))

    # ---------

    def WriteAll(self):
        for (name, collection) in self.collections.items():
            self.WriteOne(name, collection)

    def WriteOne(self, name, collection):
        # Create an empty section for each module. ConfigParser preserves 
        # the order.
        cp = ConfigParser(interpolation=None)
        paths = {self.mm.NameToPath(m) : {} for m in collection}
        cp.read_dict(paths)

        if collection.disableRunAll:
            cp[DEFAULTSECT][self.DISABLERUNALL] = repr(True)
            
        with open(os.path.join(COLLECTIONS_PATH,
                               name + self.COLLECTIONS_SUFFIX), 'w') as f:
            cp.write(f)
