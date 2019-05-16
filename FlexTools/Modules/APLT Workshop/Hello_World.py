from FTModuleClass import *

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {'moduleName'       : "Hello World",
        'moduleVersion'    : 1,
        'moduleModifiesDB' : False,
        'moduleSynopsis'   : "Report statistics about the lexicon and texts.",
        'moduleDescription'   :
u"""
Produces a report on the Lexicon and Texts in a FLEx database 
including number of words and sentences and averages.
""" }
                 
#----------------------------------------------------------------
# The main processing function

def HelloWorld(DB, report, modifyAllowed):
    report.Info("Hello APLT Workshop participants!")
    report.Warning("Bad move!")
    report.Error("Can't continue... please buy me a burger!")
    report.Error("Hello")
    
         
#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:

FlexToolsModule = FlexToolsModuleClass(runFunction = HelloWorld,
                                       docs = docs)
            
#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
