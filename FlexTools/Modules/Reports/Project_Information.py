# -*- coding: utf-8 -*-
#
#   Reports.Project_Information
#    - A FlexTools Module
#
#
#   C D Farrow
#   June 2014
#
#   Platforms: Python .NET
#

from flextoolslib import *

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name        : "Project Information",
        FTM_Version     : 1,
        FTM_ModifiesDB  : False,
        FTM_Synopsis    : "Report detailed information about the project.",
        FTM_Description :
"""
This module reports information about writing systems, custom fields, and
parts of speech.
""" }


#----------------------------------------------------------------
# The main processing function

def MainFunction(project, report, modifyAllowed):

    # Global things in the Language Project

    report.Info("Project created: %s" % project.lp.DateCreated)
    report.Info("Last modified: %s"    % project.lp.DateModified)
    report.Blank()    
 

    # Writing Systems 

    vernWSs = project.GetAllVernacularWSs()
    analWSs = project.GetAllAnalysisWSs()
    report.Info("%i Writing Systems: [Language Tag, Handle]"
                % (len(vernWSs)+len(analWSs)))
    report.Info("   Vernacular:")
    for tag in vernWSs:
        report.Info("      %s [%s, %i]%s" %
                    (project.WSUIName(tag), tag, project.WSHandle(tag),
                     " {Default}" if project.GetDefaultVernacularWS()[0] == tag else ""))

    report.Info("  Analysis:")
    for tag in analWSs:
        report.Info("      %s [%s, %i]%s" %
                    (project.WSUIName(tag), tag, project.WSHandle(tag),
                     " {Default}" if project.GetDefaultAnalysisWS()[0] == tag else ""))
    report.Blank()    


    # Custom Fields

    report.Info("Custom Fields:")
    report.Info("   Entry level:")
    for cf in project.LexiconGetEntryCustomFields():
        # Tuple of flid and user-defined name:
        report.Info("      %s [%i]" % (cf[1], cf[0]))
    report.Info("   Sense level:")
    for cf in project.LexiconGetSenseCustomFields():
        report.Info("      %s [%i]" % (cf[1], cf[0]))
    report.Blank()    


    # Grammatical Info (Parts of Speech)
    
    posList = project.GetPartsOfSpeech()
    report.Info("%i Parts of Speech:" % len(posList))
    for pos in posList:
        report.Info("    %s" % pos)


#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:

FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)

#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
