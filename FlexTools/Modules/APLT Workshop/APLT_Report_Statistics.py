# -*- coding: utf-8 -*-
#
#   Example_Report_Statistics
#    - A FlexTools Module -
#
#   Produces a report on the Lexicon and Texts in a FLEx database:
#       # of texts
#       # of sentences
#       average sentences per text
#       average words per sentence
#
#   C D Farrow
#   April 2009
#
#   Platforms: Python .NET and IronPython
#

from FTModuleClass import *

#----------------------------------------------------------------
# Configurables:


#----------------------------------------------------------------
# Documentation that the user sees:

docs = {'moduleName'       : "Example - Report Statistics",
        'moduleVersion'    : 1,
        'moduleModifiesDB' : False,
        'moduleSynopsis'   : "Report statistics about the lexicon and texts.",
        'moduleDescription'   :
u"""
Produces a report on the Lexicon and Texts in a FLEx database 
including number of words and sentences and averages.
""" }
                 
#----------------------------------------------------------------
# The main processing function

def ReportStatistics(DB, report, modifyAllowed):
    report.Info("Compiling Text statistics...")
    #report.Warning("This is a warning message!")
    #report.Error("Not enough electrons in the universe to continue!")

    report.Info("Lexicon contains:")
    report.Info("%d entries" % DB.LexiconNumberOfEntries())

    numSenses = 0
    numWithExamples = 0
    numWithDefinitions = 0
    for e in DB.LexiconAllEntries():
        for sense in e.SensesOS :
            numSenses += 1
            if DB.LexiconGetSenseDefinition(sense):
                numWithDefinitions += 1
            else:
                pass #print "Missing definition: %s" % DB.LexiconGetLexemeForm(e)
            if sense.ExamplesOS.Count > 0:
                numWithExamples += 1

    report.Info("%d senses" % numSenses)
    if numSenses > 0:
        report.Info("%d senses have definitions (%d%%)" %
                    (numWithDefinitions, numWithDefinitions*100/numSenses))
        report.Info("%d senses have examples (%d%%)" %
                    (numWithExamples, numWithExamples*100/numSenses))

    numTexts = 0
    numParagraphs = 0
    numSentences = 0
    numWords = 0
    for name, text in DB.TextsGetAll():
        #report.Info("Processing text: %s" % name)
        numTexts      += 1
        numParagraphs += text.count("\n") + 1
        numSentences  += text.count(".")
        numSentences  += text.count("?")
        numSentences  += text.count("!")
        numWords      += len(text.split())

    report.Info("Database contains:")
    report.Info("%d texts" % numTexts)
    if numTexts > 0:
        report.Info("%d paragraphs (average of %.1f per text.)" %
                    (numParagraphs, float(numParagraphs) / numTexts))
        report.Info("%d sentences (average of %.1f per paragraph.)" %
                    (numSentences, float(numSentences) / numParagraphs))
        report.Info("%d words (average of %.1f per sentence.)" %
                    (numWords, float(numWords) / numSentences))

         
#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:

FlexToolsModule = FlexToolsModuleClass(runFunction = ReportStatistics,
                                       docs = docs)
            

#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
