#
#   Export.Export_SemanticDomains_To_File
#    - A FlexTools Module -
#
#   Export the Semantic Domain list in a FLEx project to a file.
#
#   Kien-Wei Tseng
#   March 2016
#
#   Platforms: Python .NET and IronPython
#

from flextoolslib import *

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name        : "Export Semantic Domain List To File",
        FTM_Version     : 2,
        FTM_ModifiesDB  : False,
        FTM_Synopsis    : "Export the Semantic Domain list to a file.",
        FTM_Description :
"""
Export the Semantic Domain list to a file.
""" }

#----------------------------------------------------------------

def Main(project, report, modifyAllowed):

    outputFile = "SemanticDomains_{0}.txt".format(project.ProjectName())

    with open(outputFile, mode="w", encoding="utf-8") as output:
        count = 0
        for sd in project.GetAllSemanticDomains(True):
            #output.write(sd.Hvo + '\n')
            output.write(sd.ToString() + '\n')
            report.Info("Semantic Domain: %s" % sd)
            count      += 1
    report.Info("Exported {0} semantic domains to file {1}".format(
                count, outputFile),
                report.FileURL(outputFile))

#----------------------------------------------------------------

FlexToolsModule = FlexToolsModuleClass(Main, docs)
            
#----------------------------------------------------------------
if __name__ == '__main__':
    print(FlexToolsModule.Help())
