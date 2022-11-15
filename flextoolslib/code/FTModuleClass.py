#
#   Project: FlexTools
#   Module:  FTModuleClass
#
#   FlexToolsModuleClass: The class used for an installable module.
#                         See the class definition for documentation.
#
#   Craig Farrow
#   October 2010
#

# FlexTools module documentation keys. These keys must be defined in the
# docs dictionary passed to the FlexToolsModuleClass initialisation.
FTM_Name        = 'moduleName'
FTM_Version     = 'moduleVersion'
FTM_ModifiesDB  = 'moduleModifiesDB'
FTM_Synopsis    = 'moduleSynopsis'
FTM_Help        = 'moduleHelp'
FTM_Description = 'moduleDescription'

# Private - don't define these in the module
FTM_Path        = 'modulePath'
FTM_HasConfig   = 'moduleHasConfiguration'  # Note: configuration not implemented yet.


class FTM_ModuleError(Exception):
    """Exception raised for any detectable errors in a module.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message


class FlexToolsModuleClass (object):
    """
   A FlexTools module (located in the Modules directory) should define:
       FlexToolsModule = FlexToolsModuleClass(_processing_function_,
                                              _user_documentation_)

     - _processing_function_ is a function of the form:
         def _processing_function_(project, report, modifyAllowed):

           - _project_ is a FLExProject instance:
                   See flexlibs\FLExProject.py for the methods that are
                   provided.
           - _report_ is a FTReport.FTReporter instance that reports 
                   status messages:
                   report.Info(msg)
                   report.Warning(msg, reference)
                   report.Error(msg, reference)
                       - reference is an optional hyperlink to a lexical
                         entry in FLEx.
                         It is built with project.BuildGotoURL(entry)
           - _modififyAllowed_ is True if the user has permitted any kind
             of modification to the project. If this is False then the module
             should ensure that no data is modified.
             Users are warned to back up their projects before attempting 
             any modifications via a FlexTools module.

    - _user_documentation_ is a dictionary with the following keys defined:
        FTM_Name           : A short name for the module.
        FTM_Version        : The module version as a string or anything that
                             can be converted with str().
                             e.g. an integer, "1.3", "Beta release 5", etc.
        FTM_ModifiesDB     : True/False indicating whether this module
                             makes changes to the project (when the user
                             permits it.)
        FTM_Synopsis       : A description of the module's function or purpose.
        FTM_Help           : A link to a help file for this module.
        FTM_Description    : A multi-line description of the module's
                             function. Please explain the behaviour and
                             purpose clearly.
                             If relevant, include specific information about
                             how the project is modified.
    Exceptions:
        KeyError - raised if there are missing documentation keys.
    """
    __requiredDocKeys = [FTM_Name,
                      FTM_Version,
                      FTM_ModifiesDB,
                      FTM_Synopsis,
                      FTM_Description]

    def __init__(self, runFunction, docs, configuration=[]):
        if any([x not in docs for x in self.__requiredDocKeys]):
            raise FTM_ModuleError("Module documentation is missing required key.\n"\
                                   "Required keys:\n\t" + "\n\t".join(self.__requiredDocKeys))

        self.docs = docs
        self.configurationItems = configuration
        self.runFunction = runFunction

        self.docs[FTM_HasConfig] = (len(self.configurationItems) > 0)

    def GetDocs(self):
        return self.docs

    def GetConfigurables(self):
        return self.configurationItems

    def Run(self, project, report, modifyAllowed = False):
        if self.runFunction:
            # Prevent writes if not documented
            if modifyAllowed and not self.docs[FTM_ModifiesDB]:
                report.Warning("Changes are enabled, but this module doesn't allow it. Disabling changes.")
                modifyAllowed = False
            self.runFunction(project, report, modifyAllowed)

    def Help(self):
        #
        # Returns information on this module formatted as a multi-line
        # string.
        #

        result = []
        for item in list(self.docs.items()):
            result.append("%s : %s" % item)

        #if self.docs[FTM_HasConfig]:...

        return "\n".join(result)
