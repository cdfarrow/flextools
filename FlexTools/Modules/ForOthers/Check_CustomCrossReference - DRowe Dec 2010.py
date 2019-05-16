# -*- coding: cp1252 -*-

#
#   Check_CustomCrossReference - DRowe Dec 2010.py
#    - A FlexTools Module -
#
#
#
#   Platforms: Python.NET and IronPython
#

from FTModuleClass import *
from SIL.LCModel import *
from SIL.LCModel.Core.KernelInterfaces import ITsString, ITsStrBldr   


#----------------------------------------------------------------
# User documentation:

docs = {FTM_Name       : "DRowe Check Custom Cross Reference",
        FTM_Version    : 1,
        FTM_ModifiesDB : False,
        FTM_Synopsis   : "...blurb in here...",
        FTM_Help       : None,
        FTM_Description:
u"""
Full info in here....

""" }
                 
                 
def Check_CrossReferences(DB, report, modify=False):
        
        report.Info("Checking cross-references...")

        # TODO: Change this to your custom field name
        xrefFieldName = "FTFlags"
        # TODO: Change this call to specify Sense-level or Entry level custom field
        xrefField = DB.LexiconGetSenseCustomFieldNamed(xrefFieldName)
        if not xrefField:
            report.Error( "ERROR: field not found - " + xrefFieldName )
            return

        # Construct a set of all headwords (+ first gloss if there are homographs)

        allEntries = set()

        for e in DB.LexiconAllEntries():
            if e.HomographNumber:
                for sense in e.SensesOS :
                    key = " ".join((DB.LexiconGetLexemeForm(e),
                                    DB.LexiconGetSenseGloss(sense)))
                    break
            else:
                key = DB.LexiconGetLexemeForm(e)
            #print key
            if key in allEntries:
                report.Warning( "Warning: same gloss in homograph - " + key )
            allEntries.add(key)


        for e in DB.LexiconAllEntries():
            for sense in e.SensesOS :
                # Find the custom field
                crossRefs = ITsString(DB.db.GetTsStringProperty(sense.Hvo, xrefField)).Text
                if crossRefs:
                    #print ">>", crossRefs

                    # TODO: adjust to suit your cross-ref field formatting
                    xrefs = crossRefs.split(";")
                    for xr in xrefs:
                        xr = xr.strip(" ")
                        if xr in allEntries:
                            report.Info( "Found " + xr)
                        else:
                            report.Warning("Missing " + xr, DB.BuildGotoURL(e))
            
        report.Info("Done!")
         
#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:

FlexToolsModule = FlexToolsModuleClass(runFunction = Check_CrossReferences,
                                       docs = docs)


#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()

