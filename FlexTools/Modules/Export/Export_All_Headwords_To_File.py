#
#   Export.Export_All_Headwords_To_File
#    - A FlexTools Module -
#
#   Export all headwords in a FLEx project to a file.
#
#   Kien-Wei Tseng
#   April 2016
#
#   Platforms: Python .NET and IronPython
#

from flextoolslib import *

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name        : "Export All Headwords To File",
        FTM_Version     : 2,
        FTM_ModifiesDB  : False,
        FTM_Synopsis    : "Export all headwords to a file.",
        FTM_Description :
"""
Export all Headwords to a file.
""" }
                 
#----------------------------------------------------------------

def Main(project, report, modifyAllowed):

    headwordsFile = "Headwords_All_{0}.txt".format(project.ProjectName())

    headwords = []
    for e in project.LexiconAllEntries():
        headwords.append(project.LexiconGetHeadword(e))
    
    with open(headwordsFile, mode="w", encoding="utf-8") as output:
        for headword in sorted(headwords, key=lambda s: s.lower()):
            output.write(headword + '\n')

    report.Info("Exported {0} headwords to file {1}".format(
                len(headwords), headwordsFile),
                report.FileURL(headwordsFile))
    report.Info("Total lexical entries in project = {}".format(
                project.LexiconNumberOfEntries()))

#----------------------------------------------------------------

FlexToolsModule = FlexToolsModuleClass(Main, docs)
            
#----------------------------------------------------------------
if __name__ == '__main__':
    print(FlexToolsModule.Help())
    