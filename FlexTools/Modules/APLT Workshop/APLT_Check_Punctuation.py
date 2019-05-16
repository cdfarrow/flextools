# -*- coding: utf-8 -*-
#
#   Example.Check_Punctuation
#    - A FlexTools Module
#
#   Scans a FLEx database checking for good punctuation in the examples fields.
#   In particular it checks for:
#        - a single '?', '!', or '.' at the end.
#
#   An error message is added to the FTFlags (sense-level) field if database
#   changes are enabled. This allows easy filtering in FLEx to correct the errors.
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
# Configurables:

TestNumberOfEntries  = -1   # -1 for whole DB; else no. of db entries to scan

TestSuite = [
       (re.compile(r"[?!\.]{1}$"), False, "ERR:no-ending-punc"),
       (re.compile(r"[?!\.]{2,}$"), True, "ERR:too-much-punc")

       ]

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {'moduleName'       : "APLT - Check Punctuation",
        'moduleVersion'    : 1,
        'moduleModifiesDB' : True,
        'moduleSynopsis'   : "Check sentence ending punctuation in example sentences.",
        'moduleDescription':
u"""
Experimenting for APLT workshop.
""" }


#----------------------------------------------------------------
# The main processing function

def MainFunction(DB, report, modifyAllowed):
    """
    This is the main processing function.

    This example illustrates:
     - Processing over all lexical entries and their senses.
     - Adding a message to a custom field.
     - Report messages that give feedback and information to the user.
     - Report messages that include a hyperlink to the entry (for Warning & Error only).
    
    """
    report.Info("Beginning Punctuation Check")
    #report.Warning("The sky is falling!")
    #report.Error("Failed to ...")
        
    limit = TestNumberOfEntries

    if limit > 0:
        report.Warning("TEST: Scanning first " + str(limit) + " entries...")
    else:
        report.Info("Scanning " + str(DB.LexiconNumberOfEntries()) + " entries...")

    AddReportToField = modifyAllowed

    flagsField = DB.LexiconGetSenseCustomFieldNamed("FTFlags")
    if AddReportToField and not flagsField:
        report.Error("FTFlags custom field doesn't exist at Sense level")
        AddReportToField = False
    
    for e in DB.LexiconAllEntries():
        lexeme = DB.LexiconGetLexemeForm(e)
        for sense in e.SensesOS:
            for example in sense.ExamplesOS:
                if DB.LexiconGetExample(example) == None:
                    report.Warning("Blank example: " + lexeme, DB.BuildGotoURL(e))
                    continue
                for test in TestSuite:
                    funcOrRegex, result, message = test
                    if type (funcOrRegex) is not FunctionType:
                        if (funcOrRegex.search(DB.LexiconGetExample(example)) <> None) \
                          == result:
                           report.Warning(lexeme + ": " + message, DB.BuildGotoURL(e))
                           if AddReportToField:
                               #oldtag = DB.LexiconGetFieldText(sense, flagsField)
                               #DB.LexiconSetFieldText(sense, flagsField, "")
                               DB.LexiconAddTagToField(sense, flagsField, message)
           
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
