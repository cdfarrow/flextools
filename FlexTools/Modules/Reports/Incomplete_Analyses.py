# -*- coding: utf-8 -*-
#
#   Incomplete_Analyses
#    - A FlexTools Module -
#
#   C D Farrow
#   June 2014
#
#   Platforms: Python.NET and IronPython
#

from flextoolslib import *

from SIL.LCModel import ISegmentRepository
from SIL.LCModel.Core.KernelInterfaces import ITsString, ITsStrBldr

from collections import defaultdict

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Incomplete Analyses",
        FTM_Version    : 1,
        FTM_ModifiesDB : False,
        FTM_Synopsis   : "Report on analyses that have missing Morphs or Senses.",
        FTM_Help       : None,
        FTM_Description:
"""
This module reports all the words in the corpus that haven't been
fully analysed, so the user can easily find gaps in their analysis.
"""
}
                 
#----------------------------------------------------------------
def FTModule(project, report, modifyAllowed=False):

    for seg in project.ObjectsIn(ISegmentRepository):
        for analysis in seg.AnalysesRS:
            if analysis.Analysis:
                for mb in analysis.Analysis.MorphBundlesOS:
                    if not mb.MorphRA or not mb.SenseRA:
                        report.Warning("%s: Missing morphs or senses"
                                       % ITsString(mb.Owner.ChooserNameTS).Text,
                                       project.BuildGotoURL(analysis))

#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:

FlexToolsModule = FlexToolsModuleClass(runFunction = FTModule,
                                       docs = docs)
            

#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
