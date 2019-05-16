# -*- coding: utf-8 -*-
#
#   Find Incomplete Analyses
#    - A FlexTools Module -
#
#   C D Farrow
#   June 2014
#
#   Platforms: Python.NET and IronPython
#


from FTModuleClass import *
from SIL.LCModel import *
from SIL.LCModel.Core.KernelInterfaces import ITsString, ITsStrBldr

from collections import defaultdict


#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Find Incomplete Analyses",
        FTM_Version    : 1,
        FTM_ModifiesDB : False,
        FTM_Synopsis   : "Report on analyses that have missing Morphs or Senses.",
        FTM_Help       : None,
        FTM_Description:
"""
"""
}
                 
#----------------------------------------------------------------
def FTModule(DB, report, modify=False):

    for seg in DB.ObjectsIn(ISegmentRepository):
        for analysis in seg.AnalysesRS:
            if analysis.Analysis:
                for mb in analysis.Analysis.MorphBundlesOS:
                    if not mb.MorphRA or not mb.SenseRA:
                        report.Warning(u"%s: Missing morphs or senses"
                                       % ITsString(mb.Owner.ChooserNameTS).Text,
                                       DB.BuildGotoURL(analysis))

#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:

FlexToolsModule = FlexToolsModuleClass(runFunction = FTModule,
                                       docs = docs)
            

#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
