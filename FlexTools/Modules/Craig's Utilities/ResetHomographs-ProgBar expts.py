# -*- coding: utf-8 -*-
#
#   C D Farrow
#   May 2014
#
#   Platforms: Python .NET and IronPython
#

from FTModuleClass import *

from collections import defaultdict
from types import *

from System.Windows.Forms import ProgressBar

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Experiment - Progress Bar",
        FTM_Version    : 0,
        FTM_ModifiesDB : False,
        FTM_Synopsis   : "Scratch Module for experiments",
        FTM_Help       : None,
        FTM_Description: ""
}


#----------------------------------------------------------------
# The main processing function

def MainFunction(DB, report, modifyAllowed):
    """
    This is the main processing function.
    """

    if modifyAllowed:
        report.Info(u"Reseting homograph numbers...")
        report.Info(repr(dir(ProgressBar)))
        progress = ProgressBar()
        DB.lexDB.ResetHomographNumbers(progress)
        report.Info(u"Done")
        
#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:

FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)

#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
