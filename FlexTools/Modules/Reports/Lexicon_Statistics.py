# -*- coding: utf-8 -*-
#
#   Reports.Lexicon_Statistics
#    - A FlexTools Module -
#
#   Produces a report on the Lexicon:
#       number of lexemes
#       number of senses
#       number of senses with definitions
#       number of senses with examples
#
#   C D Farrow
#   April 2009
#
#   Platforms: Python .NET and IronPython
#

from FTModuleClass import *

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Lexicon Statistics",
        FTM_Version    : 2,
        FTM_ModifiesDB : False,
        FTM_Synopsis   : "Give a summary report of the lexicon.",
        FTM_Help       : None,
        FTM_Description:
u"""
Reports the number of lexemes and senses, plus
number of senses with definitions and examples.
""" }

    
#----------------------------------------------------------------
# The main processing function

def MainFunction(DB, report, modifyAllowed):
    
    global numSenses
    global numWithDefinitions
    global numWithExamples

    def __recordSenseInfo(DB, sense):
        global numSenses
        global numWithDefinitions
        global numWithExamples
        
        numSenses += 1
        if DB.LexiconGetSenseDefinition(sense):
            numWithDefinitions += 1
        if sense.ExamplesOS.Count > 0:
            numWithExamples += 1

        for subsense in sense.SensesOS:
            __recordSenseInfo(DB, subsense)


    report.Info("Lexicon contains:")
    numberEntries = DB.LexiconNumberOfEntries()
    report.Info("    %d entries" % numberEntries)
    report.ProgressStart(numberEntries)

    numSenses = 0
    numWithExamples = 0
    numWithDefinitions = 0
    for entryNumber, entry in enumerate(DB.LexiconAllEntries()):
        report.ProgressUpdate(entryNumber)
        for sense in entry.SensesOS:
            __recordSenseInfo(DB, sense)

    report.Info("    %d senses" % numSenses)
    if numSenses:
        report.Info("%d senses have definitions (%d%%)" %
                    (numWithDefinitions, numWithDefinitions*100/numSenses))
        report.Info("%d senses have examples (%d%%)" %
                    (numWithExamples, numWithExamples*100/numSenses))

#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:

FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            
#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
