# -*- coding: utf-8 -*-
#
#   Reports.Database Information
#    - A FlexTools Module
#
#
#   C D Farrow
#   June 2014
#
#   Platforms: Python .NET
#

from FTModuleClass import *

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name        : "Database Information",
        FTM_Version     : 1,
        FTM_ModifiesDB  : False,
        FTM_Synopsis    : "Reports detailed information about the database.",
        FTM_Description :
u"""
This Module reports information about writing systems, custom fields, and
parts of speech.
""" }


#----------------------------------------------------------------
# The main processing function

def MainFunction(DB, report, modifyAllowed):

    # Global things in the Language Project

    report.Info("Database created: %s" % DB.lp.DateCreated)
    report.Info("Last modified: %s"    % DB.lp.DateModified)
    report.Blank()    
 

    # Writing Systems 

    vernWSs = DB.GetAllVernacularWSs()
    analWSs = DB.GetAllAnalysisWSs()
    report.Info(u"%i Writing Systems: [Language Tag, Handle]"
                % (len(vernWSs)+len(analWSs)))
    report.Info("   Vernacular:")
    for tag in vernWSs:
        report.Info(u"      %s [%s, %i]%s" %
                    (DB.WSUIName(tag), tag, DB.WSHandle(tag),
                     u" {Default}" if DB.GetDefaultVernacularWS()[0] == tag else u""))

    report.Info("  Analysis:")
    for tag in analWSs:
        report.Info(u"      %s [%s, %i]%s" %
                    (DB.WSUIName(tag), tag, DB.WSHandle(tag),
                     u" {Default}" if DB.GetDefaultAnalysisWS()[0] == tag else u""))
    report.Blank()    


    # Custom Fields

    report.Info(u"Custom Fields:")
    report.Info(u"   Entry level:")
    for cf in DB.LexiconGetEntryCustomFields():
        # Tuple of flid and user-defined name:
        report.Info(u"      %s [%i]" % (cf[1], cf[0]))
    report.Info(u"   Sense level:")
    for cf in DB.LexiconGetSenseCustomFields():
        report.Info(u"      %s [%i]" % (cf[1], cf[0]))
    report.Blank()    


    # Grammatical Info (Parts of Speech)
    
    posList = DB.GetPartsOfSpeech()
    report.Info(u"%i Parts of Speech:" % len(posList))
    for pos in posList:
        report.Info(u"    %s" % pos)


#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:

FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)

#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
