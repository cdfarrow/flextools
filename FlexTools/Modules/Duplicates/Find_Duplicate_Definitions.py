# -*- coding: utf-8 -*-
#
#   Example.Find_Duplicate_Definitions
#    - A FlexTools Module
#
#   Scans a FLEx project checking for duplicate definitions in the same sense.
#
#   An error message is added to the FTFlags (entry-level) field if project
#   changes are enabled. This allows easy filtering in FLEx to correct the errors.
#
# Marcin Miłkowski
# May 2014
#
# Platforms: Python .NET and IronPython
#

from flextools import *

import re
from types import *

#----------------------------------------------------------------
# Configurables:

TestNumberOfEntries  = -1   # -1 for whole project; else no. of db entries to scan


#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name        : "Find Duplicate Definitions",
        FTM_Version     : 1,
        FTM_ModifiesDB  : True,
        FTM_Synopsis    : "Finds entries with duplicate definitions.",
        FTM_Description :
"""
This module scans each lexical entry and reports if there are any duplicate
definitions in the entry.

If project modification is permitted, then a warning value will be appended
to the entry-level custom field called FTFlags. This field must already exist
and should be created as a 'Single-line text' field using the 'First Analysis
Writing System.'
""" }


def list_duplicates(seq):
    seen = set()
    seen_add = seen.add
    # adds all elements it doesn't know yet to seen and all other to seen_twice
    seen_twice = set( x for x in seq if x in seen or seen_add(x) )
    # turn the set into a list (as requested)
    return list( seen_twice )

#----------------------------------------------------------------
# The main processing function

def MainFunction(project, report, modifyAllowed):
    """
    This is the main processing function.
    """

    report.Info("Beginning Definition Check")
    
    limit = TestNumberOfEntries

    if limit > 0:
        report.Warning("TEST: Scanning first " + str(limit) + " entries...")
    else:
        report.Info("Scanning " + str(project.LexiconNumberOfEntries()) + " entries...")

    AddReportToField = modifyAllowed

    flagsField = project.LexiconGetEntryCustomFieldNamed("FTFlags")
    if AddReportToField and not flagsField:
        report.Warning("FTFlags custom field doesn't exist at entry level")
        AddReportToField = False
    
    for e in project.LexiconAllEntries():
        lexeme = project.LexiconGetLexemeForm(e)
        list = []
        for sense in e.SensesOS:
            defn = project.LexiconGetSenseDefinition(sense)
            if defn:
                list.extend(defn.split("; "))			

        if list_duplicates(list):
            report.Info("Found duplicate in: " + lexeme + ": " + " ,".join(list_duplicates(list)),
                        project.BuildGotoURL(e))
            if AddReportToField:
                project.LexiconSetFieldText(e, flagsField, "Duplicate definition found: " + " ,".join(list_duplicates(list)))

        if limit > 0:
           limit -= 1
        elif limit == 0:
           break


#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:

FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)

#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
