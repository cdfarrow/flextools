# -*- coding: utf-8 -*-
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
from SIL.LCModel.Core.Text import TsStringUtils

#----------------------------------------------------------------
# Configurables:


#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Scratch - Add Text",
        FTM_Version    : 2,
        FTM_ModifiesDB : True,
        FTM_Synopsis   : "Scratch module for experiments",
        FTM_Help       : None,
        FTM_Description: 'This module creates a new text named "Dummy text", with "Hello" in the baseline.'
}
                 
#----------------------------------------------------------------
# The main processing function

def Scratch(DB, report, modify=False):

    if not modify:
        report.Error("To add text run with Modify enabled")
        return

    m_textFactory = DB.db.ServiceLocator.GetInstance(ITextFactory)
    m_stTextFactory = DB.db.ServiceLocator.GetInstance(IStTextFactory)
    m_stTxtParaFactory = DB.db.ServiceLocator.GetInstance(IStTxtParaFactory)

    text = m_textFactory.Create()           # Text is created & added to project
    stText = m_stTextFactory.Create()
    text.ContentsOA = stText                # Add StText to the Text
    stTxtPara = m_stTxtParaFactory.Create()
    stText.ParagraphsOS.Add(stTxtPara)       # Add StTxtPara to StText
    tss = TsStringUtils.MakeString("Hello", DB.db.DefaultVernWs)
    stTxtPara.Contents = tss                # Add the baseline text to StTxtPara
    tss = TsStringUtils.MakeString("Dummy text", DB.db.DefaultAnalWs)
    text.Name.AnalysisDefaultWritingSystem = tss
 
#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:

FlexToolsModule = FlexToolsModuleClass(runFunction = Scratch,
                                       docs = docs)
            

#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
