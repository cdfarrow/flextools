# -*- coding: utf-8 -*-
#
#   Lexeme_Usage_In_Corpus
#    - A FlexTools Module -
#
#   This Module counts how many times lexical entries and senses have been
#   assigned to wordforms in the text corpus. This is the total usage:
#   that is, counting every occurance even in the same wordform.
#
#   FDO/DomainImpl/OverridesLing_Lex.cs
#       EntryAnalysesCount
#       SenseAnalysesCount
#
#   C D Farrow
#   July 2016
#
#   Platforms: Python.NET
#

from flextoolslib import *

from SIL.LCModel import *
from SIL.LCModel.Core.KernelInterfaces import ITsString, ITsStrBldr   

from collections import defaultdict

#----------------------------------------------------------------
# Configurables:

# Debugging for this module
DEBUG = False

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Lexeme Usage in Corpus",
        FTM_Version    : 1,
        FTM_ModifiesDB : True,
        FTM_Synopsis   : "Count usage of lexemes in the text corpus.",
        FTM_Help       : None,
        FTM_Description:
"""
This module counts how many times lexical entries and senses have been
assigned to wordforms in the text corpus. This is the total usage:
that is, counting every occurance even in the same wordform.

The statistics can be written into the FLEx project. To do this create
an entry-level and/or a sense-level custom field called 'Entry Frequency'
and 'Sense Frequency' resepctively.
Create the fields with type 'Number'. Both custom fields are optional: 
only the one(s) that exist will be filled in. Use "Run (Modify)"
to fill these fields in.

Occurrences of variants are included under the main entry.

Remember that this data is not live, so this module should be run again to
update the usage counts after changes have been made to the corpus or
word analyses.

The report is comma-delimited so it can be copied into a spreadsheet
for analysis.
""" }


#----------------------------------------------------------------
# The main processing function

def MainFunction(project, report, modifyAllowed):

    entryUsageField = None
    senseUsageField = None

    if modifyAllowed:
        entryUsageField = project.LexiconGetEntryCustomFieldNamed("Entry Frequency")
        senseUsageField = project.LexiconGetSenseCustomFieldNamed("Sense Frequency")
    
        if not (entryUsageField or senseUsageField):
            report.Warning("Usage custom fields don't exist. Please read the module information for instructions.")

    if not modifyAllowed:
        report.Info("(Run with Modify to write the counts into custom fields. Please refer to the module information for instructions.)")
    
    report.Info("Lexeme Usage:")

    numLexemes = project.LexiconNumberOfEntries()
    report.ProgressStart(numLexemes)

    numAttested = 0
    for entryNumber, entry in enumerate(project.LexiconAllEntries()):
        report.ProgressUpdate(entryNumber)
        lexeme = project.LexiconGetHeadword(entry)
        entryTotal = 0
        for sense in entry.SensesOS:
            senseCount = project.LexiconSenseAnalysesCount(sense)
            if senseCount:
                report.Info("%s (%s), %d" % (lexeme,
                                             project.LexiconGetSenseGloss(sense),
                                             senseCount))
                entryTotal += senseCount
                
            if senseUsageField:
                project.LexiconSetFieldInteger(sense.Hvo, senseUsageField, senseCount)

        if entryUsageField:
            project.LexiconSetFieldInteger(entry.Hvo, entryUsageField, entryTotal)
            
        if entryTotal > 0:
            numAttested += 1

    if numLexemes > 0:
        report.Info("%d of %d lexemes attested in corpus (%.0f%%)" %
                    (numAttested, numLexemes, numAttested*100/numLexemes))
        
#----------------------------------------------------------------

FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            

#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
