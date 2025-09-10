#
#   Export.Export_All_Publications
#    - A FlexTools Module -
#
#   Export all headwords from each publication to one file per publication. 
#
#   Craig Farrow
#   July 2024
#

from flextoolslib import *

from _Exporters import Export_Publication

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name        : "Export All Publications",
        FTM_Version     : 1,
        FTM_ModifiesDB  : False,
        FTM_Synopsis    : "Export all headwords from each publication to a file.",
        FTM_Description :
"""
Export all headwords from each publication to a file (one file for each publication). 
Double-click on the exported message to open the file.
""" 
}


#----------------------------------------------------------------

def Main(project, report, modifyAllowed):

    for pubName in project.GetPublications():
        Export_Publication(project, report, pubName)

    report.Info(f"Total lexical entries in project: {
                project.LexiconNumberOfEntries()}")

#----------------------------------------------------------------

FlexToolsModule = FlexToolsModuleClass(Main, docs)

#----------------------------------------------------------------
if __name__ == '__main__':
    print(FlexToolsModule.Help())
