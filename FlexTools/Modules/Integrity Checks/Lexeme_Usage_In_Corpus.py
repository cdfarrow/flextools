# -*- coding: utf-8 -*-
#
#   Lexeme_Usage_In_Corpus
#    - A FlexTools Module -
#
#   Jul 2016
#   TODO - This is using old code to calculate lexeme usage; and
#          was being turned into a module to write a Frequency field.
#          That function is now in:
#               Reports.Lexeme_Usage_In_Corpus
#          Some of the calcs seem dodgey --needs more investigation.
#          Note: FW 8.1.4 Lexicon columns Number of Text Analyses
#          don't count multiple occurrences in the same sentence.  
#       ***See also Check_Number_In_Corpus in this folder
#   
#   This Module counts how many times lexical entries and senses have been
#   assigned to wordforms in the text corpus. This is the total usage:
#   that is, counting every occurance even in the same wordform.
#
#   C D Farrow
#   June 2012
#
#   Platforms: Python .NET
#

from FTModuleClass import *
from SIL.LCModel import *
from SIL.LCModel.Core.KernelInterfaces import ITsString, ITsStrBldr
from SIL.LCModel.DomainServices import SegmentServices

# FW9 TODO: Where is ITextRepository???
# from SIL.FieldWorks.FDO import ITextRepository
# from SIL.FieldWorks.FDO import IStText
# from SIL.FieldWorks.FDO import IWfiGloss, IWfiWordform, IWfiAnalysis


from collections import defaultdict

#----------------------------------------------------------------
# Configurables:

# Debugging for this module
DEBUG = False

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Lexeme Usage in Corpus",
        FTM_Version    : 3,
        FTM_ModifiesDB : True,
        FTM_Synopsis   : "Counts usage of lexemes in the text corpus.",
        FTM_Help       : None,
        FTM_Description:
u"""
This Module counts how many times lexical entries and senses have been
assigned to wordforms in the text corpus. This is the total usage:
that is, counting every occurance even in the same wordform.

The statistics can be written into the FLEx database. To do this create
an entry-level and/or a sense-level custom field called 'Frequency'.
Create the fields with type 'Number'. Both custom fields are optional: 
only the one(s) that exist will be filled in. Use "Run (Modify)"
to fill these fields in.

Occurrences of variants are included under the main entry.

Remember that this data is not live, so this Module should be run again to
update the usage counts after changes have been made to the corpus or
word analyses.

The report is comma-delimited so it can be copied into a spreadsheet
for analysis.

This Module also reports how many wordforms exist in the text corpus
and how many of these are fully analysed (i.e. have a word-form gloss
and have all morphemes assigned.)
""" }


#----------------------------------------------------------------
# The main processing function

def MainFunction(DB, report, modifyAllowed):

    entryUsageField = None
    senseUsageField = None

    if modifyAllowed:
        entryUsageField = DB.LexiconGetEntryCustomFieldNamed("Frequency")
        senseUsageField = DB.LexiconGetSenseCustomFieldNamed("Frequency")
    
        if not (entryUsageField or senseUsageField):
            report.Warning("Usage custom fields don't exist. Please read the instructions.")


    report.Info("Compiling lexeme usage statistics...")
    
    numTexts = 0
    numWordforms = 0
    numFullyAnalysed = 0
    numComplete = 0

    attestedSenses = defaultdict(int)

    numTexts = DB.ObjectCountFor(ITextRepository)
    report.ProgressStart(numTexts, "Texts")
    
    for textNumber, text in enumerate(DB.ObjectsIn(ITextRepository)):
        report.ProgressUpdate(textNumber)
        report.Info("Text: %s" % ITsString(text.Name.BestVernacularAnalysisAlternative).Text)
        if not text.ContentsOA: continue
        numberParagraphs = text.ContentsOA.ParagraphsOS.Count
        report.Info("    %i paragraph%s" % (numberParagraphs,
                                            "" if numberParagraphs==1 else "s"))
        ss = SegmentServices.StTextAnnotationNavigator(text.ContentsOA)
        for analysisOccurance in ss.GetAnalysisOccurrencesAdvancingInStText():
            if analysisOccurance.Analysis.ClassName == "PunctuationForm":
                continue

            numWordforms += 1
            glossed = True
            gloss = ""
            analysed = True
            if analysisOccurance.Analysis.ClassName == "WfiGloss":
                gloss = ITsString(analysisOccurance.Analysis.Form.AnalysisDefaultWritingSystem).Text
                if not gloss:
                    glossed = False
                wfiAnalysis = analysisOccurance.Analysis.Analysis   # Same as Owner
            elif analysisOccurance.Analysis.ClassName == "WfiAnalysis":
                glossed = False
                wfiAnalysis = analysisOccurance.Analysis
            else:
                continue

            if wfiAnalysis.IsComplete: numComplete += 1
            
            wfGlosses = []
            wfSenses = []
            analysed = wfiAnalysis.MorphBundlesOS.Count > 0
            for bundle in wfiAnalysis.MorphBundlesOS:
                if bundle.SenseRA:
                    attestedSenses[bundle.SenseRA.Hvo] += 1
                    if DEBUG:
                        wfSenses.append(bundle.SenseRA.Hvo)
                        lexGloss = ITsString(bundle.SenseRA.Gloss.BestAnalysisAlternative).Text
                        if lexGloss:
                            wfGlosses.append(lexGloss)
                        else:
                            wfGlosses.append("***")
                else:
                    analysed = False
            if DEBUG and wfGlosses:
                report.Info("  %s [%s] [%s]" % (gloss,
                                                "::".join(wfGlosses),
                                                "::".join(map(str,wfSenses))))

            if analysed and glossed:
                numFullyAnalysed += 1
            else:
                if DEBUG and not wfiAnalysis.IsComplete:
                    # TODO: which is the better thing to report?
                    # IsComplete is a more thorough test
                    # (see FDO\DomainImpl\OverridesLing_Wfi.cs)
                    # May2016 FW8.2.7: IsComplete seems faulty, and "analysed and glossed"
                    # isn't giving the right result either--more work required here.
                    pass
                    # report.Info("  (NOT COMPLETE)")

    if numWordforms > 0:
        report.Info("")
        report.Info("%d text%s" % (numTexts,
                                   "" if numTexts==1 else "s"))
        report.Info("%d wordform%s" % (numWordforms,
                                   "" if numWordforms==1 else "s"))
        if DEBUG: report.Info("%d complete" % numComplete)
        # TODO: May2016 - This stat seems dodgey -- needs work/investigation
        # report.Info("%d fully analysed (%.0f%%)" % (numFullyAnalysed,
        #                                            numFullyAnalysed*100/
        #                                               numWordforms))
    else:
        report.Info(u"No wordforms found")
        return


    report.Info("")
    report.Info("Lexeme Usage:")

    report.ProgressStart(DB.LexiconNumberOfEntries(), "Lexicon")

    numAttested = 0
    for entryNumber, entry in enumerate(DB.LexiconAllEntries()):
        report.ProgressUpdate(entryNumber)
        lexeme = ITsString(entry.HeadWord).Text
        total = 0
        for sense in entry.SensesOS:
            if attestedSenses.has_key(sense.Hvo):
                report.Info("%s (%s), %d" % (lexeme,
                                             DB.LexiconGetSenseGloss(sense),
                                             attestedSenses[sense.Hvo]))
                count = attestedSenses[sense.Hvo]
                total += count
            else:
                count = 0
            if senseUsageField:
                DB.LexiconSetFieldInteger(sense.Hvo, senseUsageField, count)

        if entryUsageField:
            DB.LexiconSetFieldInteger(entry.Hvo, entryUsageField, total)
            
        if total > 0:
            numAttested += 1

    numLexemes = DB.LexiconNumberOfEntries()
    if numLexemes > 0:
        report.Info("%d of %d lexemes attested in corpus (%.0f%%)" %
                    (numAttested, numLexemes, numAttested*100/numLexemes))
        
#----------------------------------------------------------------

FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            

#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
