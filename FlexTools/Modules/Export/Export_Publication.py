#
#   Export.Export_Publication
#    - A FlexTools Module -
#
#   Export all headwords from a publication to a file. The
#   publication name is chosen from a dialog box.
#
#   Craig Farrow
#   July 2024
#

from flextoolslib import *

from _Exporters import Export_Publication

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name        : "Export Publication",
        FTM_Version     : 1,
        FTM_ModifiesDB  : False,
        FTM_Synopsis    : "Export headwords from one publication to a file.",
        FTM_Description :
"""
Export all headwords from a publication to a file. The
publication name is chosen from a dialog box.
Double-click on the exported message to open the file.
""" }

#----------------------------------------------------------------

def Main(project, report, modifyAllowed):

    publication = FTDialogRadio("Choose a publication",
                                project.GetPublications())
    if not publication:
        report.Info("Operation cancelled")
        return

    Export_Publication(project, report, publication)

    report.Info(f"Total lexical entries in project: {
                project.LexiconNumberOfEntries()}")

#----------------------------------------------------------------

FlexToolsModule = FlexToolsModuleClass(Main, docs)
            
#----------------------------------------------------------------
if __name__ == '__main__':
    print(FlexToolsModule.Help())
    