# -*- coding: utf-8 -*-
#
#   Report_Collocations
#    - A FlexTools Module -
#
#
#   Platforms: Python .NET
#

from FTModuleClass import *


try:
    NLTK_MISSING = False
    import nltk
except ImportError:
    NLTK_MISSING = True

#----------------------------------------------------------------
# Configurables:


#----------------------------------------------------------------
# Documentation that the user sees:

docs = {'moduleName'       : "Report Collocations",
        'moduleVersion'    : 1,
        'moduleModifiesDB' : False,
        'moduleSynopsis'   : "Uses NLTK to .....",
        'moduleDescription'   :
u"""
<Add detailed description here>
""" }
                 
#----------------------------------------------------------------
# The main processing function

def MainFunction(DB, report, modifyAllowed):

    if NLTK_MISSING:
        report.Error("Requires Python nltk package; couldn't import.")
        return
        
    ## All texts in one collocation analysis:
    allTexts = "\n\n".join(list(DB.TextsGetAll(supplyName=False)))
    nText = nltk.Text(allTexts.split(), "Null")
    report.Info(nText.collocations())
    report.Blank()

    ## Each text individually analysed:
    for name, text in DB.TextsGetAll():
        report.Info(">>>> %s <<<<" % name)
        report.Info(text)
        report.Blank()

        ## Need to tokenise according to language
        ##    ## nltk.word_tokenize handles English, but not IPA letters.
        nText = nltk.Text(text.split(), name)
        report.Info(nText.collocations())
        report.Blank()
    
             
#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:

FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            

#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
