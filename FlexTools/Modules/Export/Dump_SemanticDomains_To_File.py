# -*- coding: utf-8 -*-
#
#   Reports.Dump_SemanticDomains_To_File
#    - A FlexTools Module -
#
#   Dump the Semantic Domain list in a FLEx project to a file.
#
#   Kien-Wei Tseng
#   March 2016
#
#   Platforms: Python .NET and IronPython
#

from __future__ import unicode_literals

from FTModuleClass import *
import io

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name        : "Dump Semantic Domain List To File",
        FTM_Version     : 1,
        FTM_ModifiesDB  : False,
        FTM_Synopsis    : "Dump the Semantic Domain list to a file.",
        FTM_Description :
"""
Dump the Semantic Domain list to a file.
""" }
                 
#----------------------------------------------------------------
# The main processing function

def MainFunction(project, report, modifyAllowed):

    outputFile = "SemanticDomains_{0}.txt".format(project.ProjectName())
    output = io.open(outputFile, mode="w", encoding="utf-8")

    count = 0
    for sd in project.GetAllSemanticDomains(True):
        #output.write(sd.Hvo + '\n')
        output.write(sd.ToString() + '\n')
        report.Info("Semantic Domain: %s" % sd)
        count      += 1
    report.Info("Dumped {0} Semantic Domains to file {1}".format(
                count, outputFile))
    output.close()

#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:

FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            
#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
