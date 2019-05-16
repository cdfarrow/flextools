# -*- coding: cp1252 -*-
#
#   Scratch
#    - A FlexTools Module -
#
#
#   Platforms: Python .NET and IronPython
#

import System

from FTModuleClass import *
from SIL.LCModel import *
from SIL.LCModel.Core.KernelInterfaces import ITsString, ITsStrBldr
from SIL.LCModel.Core.Text import TsStringUtils 

#----------------------------------------------------------------
# Configurables:


#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Scratch",
        FTM_Version    : "0.5.3",
        FTM_ModifiesDB : False,
        FTM_Synopsis   : "Scratch Module for experiments",
        FTM_Help       : None,
        FTM_Description: ""
}
                 
#----------------------------------------------------------------
# The main processing function

def Scratch(FlexDB, report, modify=False):
    
    AddTagToField = modify

    tagsField = FlexDB.LexiconGetEntryCustomFieldNamed(u"FTFlags")
    if not tagsField:
        report.Warning(u"FTFlags custom field doesn't exist at entry level")
    elif not FlexDB.LexiconFieldIsStringType(tagsField):
        report.Error(u"FTFlags custom field is not of type Single-line Text")
        tagsField = None
    if AddTagToField and not tagsField:
        report.Warning (u"Continuing in read-only mode")
        AddTagToField = False


    # Outputting all example sentences
    for lex in list(FlexDB.LexiconAllEntries()):
        FlexDB.LexiconSetFieldText(lex, tagsField, "test write")
        for sense in lex.SensesOS :
            for example in sense.ExamplesOS:
                if FlexDB.LexiconGetExample(example) == u"":
                    pass
                else:
                    report.Info( "\lx "+ FlexDB.LexiconGetLexemeForm(lex))
                    report.Info("Salar: " + FlexDB.LexiconGetExample(example))
                    for tr in example.TranslationsOC:
                        report.Info("English: " + FlexDB.LexiconGetExampleTranslation(tr))


         
#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:

FlexToolsModule = FlexToolsModuleClass(runFunction = Scratch,
                                       docs = docs)
            

#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
