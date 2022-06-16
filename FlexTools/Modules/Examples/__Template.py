# -*- coding: utf-8 -*-
#
#   <Module name>
#
#   <Module description>
#
#   <Author>
#   <Date>
#
#   Platforms: Python .NET and IronPython
#

from FTModuleClass import *


#----------------------------------------------------------------
# Documentation for the user:

docs = {FTM_Name       : "<Module name>",
        FTM_Version    : 1,
        FTM_ModifiesDB : False,
        FTM_Synopsis   : "<description>",
        FTM_Help       : None,
        FTM_Description: 
"""
<more detail here>
""" }


#----------------------------------------------------------------
# The main processing function

def MainFunction(project, report, modifyAllowed):
    """
    This is the main processing function.
    
    """
    #report.Info("Starting")
    #report.Warning("The sky is falling!")
    #report.Error("Failed to ...")
    

#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:

FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)

