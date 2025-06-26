#
#   Export.Export_Texts_To_File
#    - A FlexTools Module -
#
#   Export all texts in a FLEx project to a file.
#
#   Kien-Wei Tseng
#   March 2016
#
#   Platforms: Python .NET and IronPython
#

from flextoolslib import *

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name        : "Export Texts To File",
        FTM_Version     : 2,
        FTM_ModifiesDB  : False,
        FTM_Synopsis    : "Export all texts to a file.",
        FTM_Description :
"""
Export all texts to a file.
""" }
                 
#----------------------------------------------------------------

def Main(project, report, modifyAllowed):

    textsFile = "Texts_{0}.txt".format(project.ProjectName())

    with open(textsFile, mode="w", encoding="utf-8") as output:
        numTexts = 0
        for name, text in sorted(project.TextsGetAll()):
            output.write(name + '\n')
            output.write(text)
            output.write('\n\n')
            report.Info("Text: %s" % name)
            numTexts      += 1

    report.Info("Exported {0} texts to file {1}".format(
                    numTexts, textsFile),
                report.FileURL(textsFile))

#----------------------------------------------------------------

FlexToolsModule = FlexToolsModuleClass(Main, docs)
            
#----------------------------------------------------------------
if __name__ == '__main__':
    print(FlexToolsModule.Help())
