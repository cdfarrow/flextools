# -*- coding: utf-8 -*-
#
#   Utilities.Approve_Spelling_of_Numbers
#    - A FlexTools Module
#
#   Change the spelling status from Undecided to Correct for all wordforms
#   that are numbers. This includes numbers that include punctuation
#   (e.g. hyphens, for phone numbers, etc.)
#
#   C D Farrow
#   May 2014
#
#   Platforms: Python.NET
#

from flextoolslib import *

from SIL.LCModel import *
from SIL.LCModel.Core.KernelInterfaces import ITsString, ITsStrBldr   
from SIL.LCModel import SpellingStatusStates

import re
from types import *

#----------------------------------------------------------------
# Configurables:

NumberFormRegEx = re.compile(r"^\d[\d-]*$")

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name        : "Approve Spelling of Numbers",
        FTM_Version     : 2,
        FTM_ModifiesDB  : True,
        FTM_Synopsis    : "Set the spelling status to Correct for any numbers that are Undecided.",
        FTM_Description :
"""
Number forms are matched if they include hyphens.

Wordforms with status of Incorrect are not changed.
""" }


#----------------------------------------------------------------
# The main processing function

def MainFunction(project, report, modifyAllowed):

    report.Info("Approving spelling of numbers...")
    if not modifyAllowed:
        report.Info("Run with project changes allowed to actually change the status.")
    
    for w in project.ObjectsIn(IWfiWordformRepository):
        if w.SpellingStatus == SpellingStatusStates.undecided:
            form = ITsString(w.Form.BestVernacularAlternative).Text
            if NumberFormRegEx.match(form):
                report.Info(form, project.BuildGotoURL(w))
                if modifyAllowed:
                    w.SpellingStatus = SpellingStatusStates.correct

#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:

FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)

#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
