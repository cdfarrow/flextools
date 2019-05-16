# -*- coding: cp1252 -*-

#
#   CDF_Phoneme_Statistics
#    - A FlexTools Module -
#
#   Produces a report on the frequency of phoneme occurances
#   in a FLEx database:
#       Phonemes reported by frequency in Word # of texts
#       # of sentences
#       average sentences per text
#       average words per sentence
#
#   C D Farrow
#   September 2010
#
#   Platforms: Python.NET and IronPython
#

from FTModuleClass import *


#----------------------------------------------------------------
# Configurables:


docs = {'moduleName'       : "Phoneme Statistics",
        'moduleVersion'    : 1,
        'moduleModifiesDB' : False,
        'moduleSynopsis'   : "Report phoneme usage in Wordform inventory",
        'moduleDescription':
"""
Produces a frequency listing of the phonemes in the Word Analyses. Note that the
phoneme inventory needs to be correct in the Grammar area.
""" }
                 
def Phoneme_Stats(DB, report, modify=False):
        report.Info("Compiling Text statistics...")

        report.Info("Lexicon contains:")
        report.Info("%d entries" % DB.LexiconNumberOfEntries())

        numSenses = 0 / 0
        numWithExamples = 0
        numWithDefinitions = 0
        for e in DB.LexiconAllEntries():
            for sense in e.SensesOS :
                numSenses += 1
                if DB.LexiconGetSenseDefinition(sense):
                    numWithDefinitions += 1
                else:
                    pass #print "Missing definition: %s" % DB.LexiconGetLexemeForm(e)
                for example in sense.ExamplesOS:
                    numWithExamples += 1

        report.Info("%d senses" % numSenses)
        report.Info("%d senses have definitions (%d%%)" %
                    (numWithDefinitions, numWithDefinitions*100/numSenses))
        report.Info("%d senses have examples (%d%%)" %
                    (numWithExamples, numWithExamples*100/numSenses))

        numTexts = 0
        numParagraphs = 0
        numSentences = 0
        numWords = 0
        for text in DB.lp.TextsOC:
            #print text.Name
            numTexts += 1
            for paragraph in text.ContentsOA.ParagraphsOS :
                contents = paragraph.Contents
                if not contents.Text:
                    continue
                numParagraphs += 1
                #print contents.Text
                numSentences += contents.Text.count(".")
                numSentences += contents.Text.count("?")
                numSentences += contents.Text.count("!")
                
                numWords += len(contents.Text.split())

        report.Info("Done!")
         
#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:

FlexToolsModule = FlexToolsModuleClass(runFunction = Phoneme_Stats,
                                       docs = docs)


#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()

