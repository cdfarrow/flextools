# -*- coding: utf-8 -*-
#
#   Reports.Dump_Texts_To_File
#    - A FlexTools Module -
#
#   Dump all Texts in a FLEx project to a file.
#
#   Kien-Wei Tseng
#   March 2016
#
#   Platforms: Python .NET and IronPython
#

from flextools import *
import io

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name        : "Dump Texts To File",
        FTM_Version     : 1,
        FTM_ModifiesDB  : False,
        FTM_Synopsis    : "Dump all texts to file.",
        FTM_Description :
"""
Dump all texts to file.
""" }
                 
#----------------------------------------------------------------
# The main processing function

def MainFunction(project, report, modifyAllowed):

    textsFile = "Texts_{0}.txt".format(project.ProjectName())
    output = io.open(textsFile, mode="w", encoding="utf-8")

    numTexts = 0
    for name, text in sorted(project.TextsGetAll()):
        output.write(name + '\n')
        output.write(text)
        output.write('\n\n')
        report.Info("Text: %s" % name)
        numTexts      += 1
    report.Info("Dumped {0} texts to file {1}".format(numTexts, textsFile))
    output.close()

#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:

FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            
#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
