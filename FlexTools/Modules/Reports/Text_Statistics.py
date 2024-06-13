#
#   Reports.Text_Statistics
#    - A FlexTools Module -
#
#   Produces a word-count report of the Texts in a FLEx project:
#       Number of words
#       Number of sentences
#       Average words per sentence
#
#   C D Farrow
#   December 2011
#
#   Platforms: Python .NET and IronPython
#

from flextoolslib import *

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name        : "Text Statistics",
        FTM_Version     : 1,
        FTM_ModifiesDB  : False,
        FTM_Synopsis    : "Give a summary report of all the texts.",
        FTM_Description :
"""
Produces a word-count report of each individual text,
plus average numbers of words, sentences and paragraphs.
""" }
                 
#----------------------------------------------------------------
# The main processing function

def MainFunction(project, report, modifyAllowed):

    numTexts = 0
    numParagraphs = 0
    numSentences = 0
    numWords = 0
    for name, text in project.TextsGetAll():
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
                     numWords / numSentences,
                     numWords / numTexts))
    if numParagraphs > 0:
        report.Info("%d sentences (average of %.1f per paragraph.)" %
                    (numSentences, numSentences / numParagraphs))
    if numTexts > 0:
        report.Info("%d paragraphs (average of %.1f per text.)" %
                    (numParagraphs, numParagraphs / numTexts))

         
#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:

FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            
#----------------------------------------------------------------
if __name__ == '__main__':
    print(FlexToolsModule.Help())
