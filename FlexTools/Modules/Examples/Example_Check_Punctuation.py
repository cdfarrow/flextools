#
#   Example.Check_Punctuation
#    - A FlexTools Module
#
#   Scans a Fieldworks project checking for good punctuation in the 
#   examples fields.
#   In particular it checks for:
#        - a single '?', '!', or '.' at the end.
#
#   An error message is added to the FTFlags (sense-level) field if project
#   changes are enabled. This allows easy filtering in FLEx to correct 
#   the errors.
#
# C D Farrow
# July 2008
#
# Platforms: Python .NET and IronPython
#

from flextoolslib import *

import re
from types import *

#----------------------------------------------------------------
# Configurables:

TestNumberOfEntries  = -1   # -1 for whole project; else no. of lexical entries to scan

TestSuite = [
       (re.compile(r"[?!\.]{1}$"), False, "ERR:no-ending-punc"),
       (re.compile(r"[?!\.]{2,}$"), True, "ERR:too-much-punc")
       ]

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Example - Check Punctuation",
        FTM_Version    : 1,
        FTM_ModifiesDB : True,
        FTM_Synopsis   : "Check sentence ending punctuation in example sentences.",
        FTM_Help       : None,
        FTM_Description:
"""
This module checks for missing or too many of the characters '?', '!' and '.'

If project modification is permitted, then a warning value will be appended
to the sense-level custom field called FTFlags. This field must already exist
and should be created as a 'Single-line text' field using the 'First Analysis
Writing System.'
""" }


#----------------------------------------------------------------
# The main processing function

def Main(project, report, modifyAllowed):
    """
    This is the main processing function.

    This example illustrates:
     - Processing over all lexical entries and their senses.
     - Adding a message to a custom field.
     - Report messages that give feedback and information to the user.
     - Report messages that include a hyperlink to the entry (for Warning & Error only).
    
    """
    report.Info("Beginning Punctuation Check")
    
    limit = TestNumberOfEntries

    if limit > 0:
        report.Warning("TEST: Scanning first %i entries..." % limit)
        report.ProgressStart(limit)
    else:
        numEntries = project.LexiconNumberOfEntries()
        report.Info("Scanning %i entries..." % numEntries)
        report.ProgressStart(numEntries)

    AddReportToField = modifyAllowed

    flagsField = project.LexiconGetSenseCustomFieldNamed("FTFlags")
    if AddReportToField and not flagsField:
        report.Error("FTFlags custom field doesn't exist at Sense level")
        AddReportToField = False

    for entryNumber, entry in enumerate(project.LexiconAllEntries()):
        report.ProgressUpdate(entryNumber)
        lexeme = project.LexiconGetLexemeForm(entry)
        for sense in entry.SensesOS:
            for example in sense.ExamplesOS:
                exampleSentence = project.LexiconGetExample(example) 
                if not exampleSentence:
                    report.Warning("Blank example: " + lexeme, 
                                   project.BuildGotoURL(entry))
                    continue
                for test in TestSuite:
                    funcOrRegex, result, message = test
                    if type (funcOrRegex) is not FunctionType:
                        if (funcOrRegex.search(exampleSentence) != None) \
                          == result:
                           report.Warning(lexeme + ": " + message, 
                                          project.BuildGotoURL(entry))
                           if AddReportToField:
                               project.LexiconAddTagToField(sense, flagsField, message)
           
        if limit > 0:
           limit -= 1
        elif limit == 0:
           break


#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:

FlexToolsModule = FlexToolsModuleClass(runFunction = Main,
                                       docs = docs)

#----------------------------------------------------------------
if __name__ == '__main__':
    print(FlexToolsModule.Help())
