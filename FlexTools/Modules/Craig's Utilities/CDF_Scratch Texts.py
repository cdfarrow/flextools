# -*- coding: cp1252 -*-
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
from SIL.LCModel import *
from SIL.LCModel.Core.KernelInterfaces import ITsString, ITsStrBldr

#----------------------------------------------------------------
# Configurables:


#----------------------------------------------------------------
# Documentation that the user sees:

docs = {'moduleName'       : "Scratch - Texts",
        'moduleVersion'    : 0,
        'moduleModifiesDB' : False,
        'moduleSynopsis'   : "Scratch Module for experiments",
        'moduleDescription'   : ""
}
                 
#----------------------------------------------------------------
# The main processing function

def Scratch(DB, report, modify=False):

    report.Info("%d lexical entries" % DB.LexiconNumberOfEntries())

    # report.Info(str(DB.ObjectCountFor(ILexEntryRepository)))
    # for le in DB.ObjectsIn(ILexEntryRepository):
        # report.Info(le.ReferenceName)


    for entry in DB.LexiconAllEntries():
        report.Info("Entry %s: %i senses" % \
                        (entry.ReferenceName,
                         entry.SensesOS.Count))

    report.Info("Texts: %i" % (DB.ObjectCountFor(ITextRepository)))
    for text in DB.ObjectsIn(ITextRepository):
        report.Info(DB.BestStr(text.Name))

    texts = DB.TextsGetAll(supplyText=False)
    for t in texts:
        report.Info(t)
    
    report.Info("Compiling Text statistics...")

    numTexts = 0
    numParagraphs = 0
    numSentences = 0
    numWords = 0

    for name, text in DB.TextsGetAll():
        report.Info("Processing text: %s" % name)
        numTexts += 1
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

FlexToolsModule = FlexToolsModuleClass(runFunction = Scratch,
                                       docs = docs)
            

#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
