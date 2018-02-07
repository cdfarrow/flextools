# -*- coding: utf-8 -*-
#
#   Reports.Dump_All_Headwords_To_File
#    - A FlexTools Module -
#
#   Dump all Headwords in a FLEx database to file.
#
#   Kien-Wei Tseng
#   April 2016
#
#   Platforms: Python .NET and IronPython
#

from FTModuleClass import *
import codecs

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name        : "Dump All Headwords To File",
        FTM_Version     : 1,
        FTM_ModifiesDB  : False,
        FTM_Synopsis    : "Dump all Headwords to file.",
        FTM_Description :
u"""
Dump all Headwords to file.
""" }
                 
#----------------------------------------------------------------
# The main processing function

def MainFunction(DB, report, modifyAllowed):

    headwordsFile = "Headwords_All_{0}.txt".format(DB.db.ProjectId.UiName)
    output = codecs.open(headwordsFile, mode="w", encoding="utf8")
    headwords = []
    for e in DB.LexiconAllEntries():
        headwords.append(DB.LexiconGetHeadword(e))
    
    numHeadwords = 0
    for headword in sorted(headwords, key=lambda s: s.lower()):
        output.write(headword + '\r\n')
        numHeadwords += 1
    report.Info("Dumped {0} headwords to file {1}".format(numHeadwords, headwordsFile))
    report.Info("DB.LexiconNumberOfEntries = " + str(DB.LexiconNumberOfEntries()))
    output.close()		
#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:

FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            
#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
    