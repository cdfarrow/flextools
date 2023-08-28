# -*- coding: utf-8 -*-
#
#   Export.Export_All_Headwords_To_File
#    - A FlexTools Module -
#
#   Export all Headwords in a FLEx project to a file.
#
#   Kien-Wei Tseng
#   April 2016
#
#   Platforms: Python .NET and IronPython
#

from flextoolslib import *
import io

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name        : "Export All Headwords To File",
        FTM_Version     : 1,
        FTM_ModifiesDB  : False,
        FTM_Synopsis    : "Export all headwords to file.",
        FTM_Description :
"""
Export all Headwords to a file.
""" }
                 
#----------------------------------------------------------------
# The main processing function

def MainFunction(project, report, modifyAllowed):

    headwordsFile = "Headwords_All_{0}.txt".format(project.ProjectName())
    output = io.open(headwordsFile, mode="w", encoding="utf-8")
    headwords = []
    for e in project.LexiconAllEntries():
        headwords.append(project.LexiconGetHeadword(e))
    
    numHeadwords = 0
    for headword in sorted(headwords, key=lambda s: s.lower()):
        output.write(headword + '\n')
        numHeadwords += 1
    report.Info("Exported {0} headwords to file {1}".format(
                numHeadwords, headwordsFile))
    report.Info("Total Lexical Entries in Project = {}".format(
                project.LexiconNumberOfEntries()))
    output.close()		

#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:

FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            
#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
    