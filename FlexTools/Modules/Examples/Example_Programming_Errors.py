# -*- coding: utf-8 -*-
#
#   Example_Programming_Errors
#    - A FlexTools Module -
#
#   Illustrates some programming errors to show how FlexTools handles them.
#
#   C D Farrow
#   January 2014
#
#   Platforms: Python .NET
#

from FTModuleClass import *

#----------------------------------------------------------------
# Configurables:


#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name            : "Example - Programming Errors",
        FTM_Version         : 1,
        FTM_ModifiesDB      : False,
        FTM_Synopsis        : "Illustrates some programming errors.",
        FTM_Help            : None,
        FTM_Description     :
u"""
Run this Module to generate a run-time error. Comment out or fix the
error lines to reach the next error.
""" }
                 
#----------------------------------------------------------------
# The main processing function

def MainFunction(DB, report, modifyAllowed):

    ##coffeeShops === 0         ## Uncomment for syntax error
    coffeeShops = 0

    report.Info("Name error...")
    report.Info("%d coffee shops" % numEntries)

    report.Info("Division by zero error...")
    report.Info("%d coffee beans per coffee shop" % (10000 / coffeeShops))

    report.Info("Type error...")
    report.Info("%d coffee beans per coffee shop" % 10000 / coffeeShops)

    
             
#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:

FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            

#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
