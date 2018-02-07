#
#   Project: FlexTools
#   Module:  FTModuleClass
#
#   FlexToolsModuleClass: The class used for an installable Module.
#                         See the class definition for documentation.
#
#   Craig Farrow
#   October 2010
#

import exceptions

# FlexTools Module documentation keys. These keys must be defined in the
# docs dictionary passed to the FlexToolsModuleClass initialisation.
FTM_Name        = 'moduleName'
FTM_Version     = 'moduleVersion'
FTM_ModifiesDB  = 'moduleModifiesDB'
FTM_Synopsis    = 'moduleSynopsis'
FTM_Help        = 'moduleHelp'
FTM_Description = 'moduleDescription'

# Private - don't define these in the Module
FTM_Path        = 'modulePath'
FTM_HasConfig   = 'moduleHasConfiguration'  # Note: configuration not implemented yet.


class FTM_ModuleError(Exception):
    """Exception raised for any detectable errors in a Module.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message


class FlexToolsModuleClass (object):
    """
   A FlexTools Module (located in the Modules directory) should define:
       FlexToolsModule = FlexToolsModuleClass(_processing_function_,
                                              _user_documentation_)

     - _processing_function_ is a function of the form:
         def _processing_function_(DB, report, modificationAllowed):

           - DB is a FLExDBAccess instance:
                   See FlexLibs\FLExDBAccess.py for the available interface.
           - report is for reporting status messages:
                   report.Info(msg)
                   report.Warning(msg, reference)
                   report.Error(msg, reference)
                       - reference is an optional hyperlink to a lexical
                         entry in FLEx.
                         It is built with DB.BuildGotoURL(entry)
           - modificationAllowed is True if the user has permitted any kind
             of database modification. If this is False then the module
             should ensure that no data is modified.
             Users should be warned to back up their database before
             attempting any modifications to the database via a FlexTools
             module.

    - _user_documentation_ is a dictionary with the following keys defined:
        FTM_Name           : A short name for the Module.
        FTM_Version        : The Module version as a string or anything that 
                             can be converted with str().
                             e.g. an integer, "1.3", "Beta release 5", etc.
        FTM_ModifiesDB     : True/False indicating whether this Module
                             makes changes to the database (when the user
                             permits it.) 
        FTM_Synopsis       : A description of the module's function or purpose.
        FTM_Help           : A link to a help file for this Module.
        FTM_Description    : A multi-line description of the Module's
                             function. Please explain the behaviour and
                             purpose clearly.
                             If relevant, include specific information about
                             how the database is modified.
    Exceptions:
        KeyError - raised if there are missing documentation keys.
    """
    __validDocKeys = [FTM_Name,
                      FTM_Version,
                      FTM_ModifiesDB,
                      FTM_Synopsis,
                      FTM_Description]
    
    def __init__(self, runFunction, docs, configuration=[]):
        if any([x not in docs for x in self.__validDocKeys]):
            raise FTM_ModuleError, "Module documentation is missing required key.\n"\
                                   "Required keys:\n\t" + "\n\t".join(self.__validDocKeys)
        
        self.docs = docs
        self.configurationItems = configuration
        self.runFunction = runFunction
                 
        self.docs[FTM_HasConfig] = (len(self.configurationItems) > 0)

    def GetDocs(self):
        return self.docs

    def GetConfigurables(self):
        return self.configurationItems

    def Run(self, DB, report, modify = False):
        if self.runFunction:
            # Prevent writes if not documented
            if not self.docs[FTM_ModifiesDB]:       
                modify = False
            self.runFunction(DB, report, modify)

    def Help(self):
        "Prints information on this FT Module to the console."
        if self.runFunction:
            help(self.runFunction)
        for key, value in self.docs.items():
            print key, ":", value
        print
        if self.docs[FTM_HasConfig]:
            print "Configuration:"
            print self.configurationItems
