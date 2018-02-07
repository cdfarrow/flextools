# -*- coding: utf-8 -*-
#
#   Reports.Text_Statistics
#    - A FlexTools Module -
#
#   Produces a word-count report of the Texts in a FLEx database:
#       Number of words
#       Number of sentences
#       Average words per sentence
#
#   C D Farrow
#   December 2011
#
#   Platforms: Python .NET and IronPython
#

from FTModuleClass import *

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name        : "Text Statistics",
        FTM_Version     : 1,
        FTM_ModifiesDB  : False,
        FTM_Synopsis    : "Give a summary report of all the texts.",
        FTM_Description :
u"""
Produces a word-count report of each individual text,
plus average numbers of words, sentences and paragraphs.
""" }
                 
#----------------------------------------------------------------
# The main processing function

def MainFunction(DB, report, modifyAllowed):

    numTexts = 0
    numParagraphs = 0
    numSentences = 0
    numWords = 0
    for name, text in DB.TextsGetAll():
        report.Info("Text: %s" % name)
        numTexts      += 1
        numParagraphs += text.count("\n") + 1
        numSentences  += text.count(".")
        numSentences  += text.count("?")
        numSentences  += text.count("!")
        thisTextWords = len(text.split())
        report.Info("Word count = %i" % thisTextWords)
        numWords      += thisTextWords

    report.Info("Total %d texts" % numTexts)
    if numSentences > 0:
        report.Info("%d words (average of %.1f per sentence; %.1f per text.)" %
                    (numWords,
                     float(numWords) / numSentences,
                     float(numWords) / numTexts))
    if numParagraphs > 0:
        report.Info("%d sentences (average of %.1f per paragraph.)" %
                    (numSentences, float(numSentences) / numParagraphs))
    if numTexts > 0:
        report.Info("%d paragraphs (average of %.1f per text.)" %
                    (numParagraphs, float(numParagraphs) / numTexts))

         
#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:

FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            
#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
