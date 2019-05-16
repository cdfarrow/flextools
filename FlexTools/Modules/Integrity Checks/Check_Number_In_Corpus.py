# -*- coding: utf-8 -*-
#
#   Check_Number_in_Corpus
#    - A FlexTools Module -
#
#   Uses two different methods to calculate the number of occurences of each
#   lexeme in the corpus. Produces a report on any inconsistencies between
#   the two calculations, which may indicate corrupted data, or an incomplete
#   calculation algorithm.
#
#   C D Farrow
#   May 2014
#
#   Platforms: Python.NET and IronPython
#

from FTModuleClass import *
from SIL.LCModel import *

from collections import defaultdict

#from SIL.LCModel.Core.Phonology import ISegmentRepository

#FW9 TODO - I can't find from where to import ISegmentRepository
# from SIL.FieldWorks.FDO import ISegmentRepository 

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Check Number in Corpus",
        FTM_Version    : 1,
        FTM_ModifiesDB : False,
        FTM_Synopsis   : "Check consistency of internal links between lexemes and texts.",
        FTM_Help       : None,
        FTM_Description:
"""
This module uses two different methods to calculate the number of 
occurences of each lexeme in the corpus. Produces a report on any
inconsistencies between the two calculations, which may indicate 
corrupted data, or an incomplete calculation algorithm.
"""
}
                 
#----------------------------------------------------------------
def CheckNumberInCorpus(DB, report, modify=False):

    # First record lexeme uses from the texts.

    occurrenceCount = defaultdict(int)
    for seg in DB.ObjectsIn(ISegmentRepository):
        for analysis in seg.AnalysesRS:
            if analysis.Analysis:
                for mb in analysis.Analysis.MorphBundlesOS:
                    # MorphRA links to the variant entry not the main entry
                    # which is what we want to count here.
                    # (SenseRA links to the main entry.)
                    if mb.MorphRA:
                        occurrenceCount[mb.MorphRA.Owner.Guid] += 1

    # Then compare with EntryAnalysesCount()
    
    for entry in DB.LexiconAllEntries():
        lexeme = DB.LexiconGetLexemeForm(entry)
        count = DB.LexiconEntryAnalysesCount(entry)
        if occurrenceCount[entry.Guid] < count:
            report.Warning(u"%s: Texts (%i) <> EntryAnalysesCount (%i)"
                        % (lexeme, occurrenceCount[entry.Guid], count))
        elif occurrenceCount[entry.Guid] <> count:
            report.Info(u"%s: Texts (%i) <> EntryAnalysesCount (%i)"
                        % (lexeme, occurrenceCount[entry.Guid], count))


#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:

FlexToolsModule = FlexToolsModuleClass(runFunction = CheckNumberInCorpus,
                                       docs = docs)
            

#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
