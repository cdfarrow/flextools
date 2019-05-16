# -*- coding: cp1252 -*-
#
#   Scratch
#    - A FlexTools Module -
#
#
#   Platforms: Python .NET and IronPython
#

from FTModuleClass import *
from SIL.LCModel import *
from SIL.LCModel.Core.KernelInterfaces import ITsString, ITsStrBldr   

#----------------------------------------------------------------
# Configurables:


#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Scratch - Lexical Relations",
        FTM_Version    : 0,
        FTM_ModifiesDB : False,
        FTM_Synopsis   : "Scratch Module for experiments",
        FTM_Help       : None,
        FTM_Description: ""
}
                 
#----------------------------------------------------------------
# The main processing function

def Scratch(DB, report, modify=False):

    report.Info("%d lexical relations" % DB.ObjectCountFor(ILexReferenceRepository))

    for lrt in DB.ObjectsIn(ILexRefTypeRepository):
        if (lrt.MembersOC.Count > 0):
            report.Info(DB.BestStr(lrt.Name))
            for lr in lrt.MembersOC:
                report.Info("[")
                for target in lr.TargetsRS:
                    if target.ClassID == LexEntryTags.kClassId:
                        report.Info("    LexEntry: %s" % (DB.LexiconGetLexemeForm(target)))
                    else: # I think you can only have LexEntry or LexSense 
                          # in a relation
                        report.Info("    LexSense: %s [%s]" % 
                                (DB.LexiconGetSenseGloss(target),
                                 DB.LexiconGetSensePOS(target)))
                report.Info("]")

         
#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:

FlexToolsModule = FlexToolsModuleClass(runFunction = Scratch,
                                       docs = docs)
            

#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
