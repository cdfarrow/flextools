# -*- coding: utf-8 -*-
#
#
# C D Farrow
# July 2008
#
# Platforms: Python .NET and IronPython
#

from FTModuleClass import *

import re
from types import *

#----------------------------------------------------------------

# A mapping from language name to sort order

LanguagesOrder = [
       ("English",  1),
       ("French",   2),
       ("Spanish",  3),
       ]

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {'moduleName'       : "Sense Level Sort",
        'moduleVersion'    : 1,
        'moduleModifiesDB' : True,
        'moduleSynopsis'   : "<description here>",
        'moduleDescription':
u"""
<more detail here>
""" }


#----------------------------------------------------------------
# The main processing function

def MainFunction(DB, report, modifyAllowed):
    """
    This is the main processing function.
    
    """
    #report.Info("Starting")
    #report.Warning("The sky is falling!")
    #report.Error("Failed to ...")
    
    UpdateSortField = modifyAllowed

    languageFieldID = DB.LexiconGetSenseCustomFieldNamed("Language")
    if not languageFieldID:
        report.Error("Language custom field doesn't exist at Sense level.")
        return
        
    sortFieldID = DB.LexiconGetSenseCustomFieldNamed("LanguageSort")
    if UpdateSortField and not sortFieldID:
        report.Error("LanguageSort custom field doesn't exist at Sense level.")
        UpdateSortField = False
    
    for e in DB.LexiconAllEntries():
        lexeme = DB.LexiconGetLexemeForm(e)
        for sense in e.SensesOS:
            language = DB.GetCustomFieldValue(sense, languageFieldID)
            try:
                sortKey = LanguagesOrder[language]
            except KeyError:
                report.error("%s not in language lookup table." % language)
                continue
            if UpdateSortField:
                DB.LexiconSetFieldInteger(sense, sortFieldID, sortKey)


#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:

FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)

#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
