# -*- coding: utf-8 -*-
#
#   Reports.Dump_Published_Headwords_To_File
#    - A FlexTools Module -
#
#   Dump all Headwords in a FLEx project to a file.
#
#   Kien-Wei Tseng
#   April 2016
#
#   Platforms: Python .NET and IronPython
#

from __future__ import unicode_literals

from FTModuleClass import *
import io

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name        : "Dump Published Headwords To File",
        FTM_Version     : 1,
        FTM_ModifiesDB  : False,
        FTM_Synopsis    : "Dump published Headwords to file.",
        FTM_Description :
"""
Dump all headwords to a file if they are marked to be published (PublishIn field has at least
one value.)
""" }
                 
#----------------------------------------------------------------
# The main processing function

def MainFunction(project, report, modifyAllowed):

    headwordsFile = "Headwords_Published_{0}.txt".format(project.ProjectName())
    output = io.open(headwordsFile, mode="w", encoding="utf-8")
    headwords = []
    for e in project.LexiconAllEntries():
        if project.LexiconGetPublishInCount(e) > 0:
            headwords.append(project.LexiconGetHeadword(e))
    numHeadwords = 0
    for headword in sorted(headwords, key=lambda s: s.lower()):
        output.write(headword + '\n')
        numHeadwords += 1
    report.Info("Dumped {0} headwords to file {1}".format(
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
    