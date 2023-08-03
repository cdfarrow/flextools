# -*- coding: utf-8 -*-
#
#   Check_Count_of_Lexemes_in_Corpus
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

from flextoolslib import *

from SIL.LCModel import ISegmentRepository

from collections import defaultdict


#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Check Count of Lexemes in Corpus",
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
def CheckNumberInCorpus(project, report, modifyAllowed=False):

    # First record lexeme uses from the texts.

    occurrenceCount = defaultdict(int)
    for seg in project.ObjectsIn(ISegmentRepository):
        for analysis in seg.AnalysesRS:
            if analysis.Analysis:
                for mb in analysis.Analysis.MorphBundlesOS:
                    # MorphRA links to the variant entry not the main entry
                    # which is what we want to count here.
                    # (SenseRA links to the main entry.)
                    if mb.MorphRA:
                        occurrenceCount[mb.MorphRA.Owner.Guid] += 1

    # Then compare with EntryAnalysesCount()
    
    for entry in project.LexiconAllEntries():
        lexeme = project.LexiconGetLexemeForm(entry)
        count = project.LexiconEntryAnalysesCount(entry)
        if occurrenceCount[entry.Guid] < count:
            report.Warning("%s: Texts (%i) < EntryAnalysesCount (%i)"
                        % (lexeme, occurrenceCount[entry.Guid], count))
        elif occurrenceCount[entry.Guid] != count:
            report.Info("%s: Texts (%i) != EntryAnalysesCount (%i)"
                        % (lexeme, occurrenceCount[entry.Guid], count))


#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:

FlexToolsModule = FlexToolsModuleClass(runFunction = CheckNumberInCorpus,
                                       docs = docs)
            

#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
