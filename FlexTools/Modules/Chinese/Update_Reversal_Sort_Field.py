# -*- coding: utf-8 -*-
#
#   Chinese.Update Reversal Sort Fields
#    - A FlexTools Module -
#
#   Finds the Chinese Reversal Index and uses the Hanzi field and 
#   Pinyin Numbered fields to populate the Sort field. See the 
#   documentation below for the Writing System codes.
#
#   C D Farrow
#   May 2011
#
#   Platforms: Python .NET and IronPython
#

from __future__ import unicode_literals
from builtins import str

from flextoolslib import *

import site
site.addsitedir(r"Lib")

from ChineseUtilities import SortStringDB, ChineseWritingSystems

#----------------------------------------------------------------
# Documentation for the user:

docs = {FTM_Name       : "Update Reversal Index Sort Field",
        FTM_Version    : "4.0",
        FTM_ModifiesDB : True,
        FTM_Synopsis   : "Updates the Chinese sort field in the Chinese Reversal Index. Sorts by pronunciation.",
        FTM_Help       : r"Doc\Chinese Utilities Help.pdf",
        FTM_Description:
"""
This module sets the sort field in the Chinese Reversal Index ('Chinese, Mandarin (China)' (zh-CN))

The sort field (zh-CN-x-zhsort) is generated from the Chinese Hanzi (zh-CN) field and
Pinyin Numbered (zh-CN-x-pyn) field.

The three writing systems mentioned above must be configured in FLEx
under Tools | Configure | Setup Writing Systems. Note that fields using
the old 'cmn' locale are also supported, but this locale code should not be used in
new projects.

The Pinyin tone number field should first be generated from the Hanzi
(zh-CN) field using either the Update_Tonenumber_Fields FLExTools Module
or the BulkEdit_HZ_2_Tonenumber transducer.

The sort field produced by this Module orders Chinese by pronunciation, then
by stroke count, and finally by stroke order. This follows the ordering in
现代汉语词典 (XianDai HanYu CiDian). Thus:

 - san < sen < shan < sheng < si < song: 三 < 森 < 山 < 生 < 四 < 送

 - lu < lü < luan < lüe: 路 < 绿 < 乱 < 掠

 - (stroke count) 录 < 录音 < 路 < 路口

 - (stroke order) zhi4 with 8 strokes: 郅 < 制 < 质 < 治

See Chinese Utilities Help.pdf for detailed information on configuration and usage.
""" }
                 
#----------------------------------------------------------------
# The main processing function

UpdatedSortStrings = 0

def UpdateReversalSortFields(project, report, modifyAllowed=False):

    
    def __WriteSortString(project, entry):
        global UpdatedSortStrings
        # Note that project is passed to each of these local functions otherwise
        # project is treated as a global and isn't released for garbage collection.
        # That keeps the project locked so FT has to be restarted to use
        # that project again.

        hz = project.ReversalGetForm(entry, ChineseWS)
        tn = project.ReversalGetForm(entry, ChineseTonenumWS)
        ss = project.ReversalGetForm(entry, ChineseSortWS)

        newSortString, msg = SortDB.CalculateSortString(hz, tn, ss)
        if msg:
            report.Warning("    %s: %s" % (hz, msg),
                           project.BuildGotoURL(entry))
        if newSortString is not None:
            report.Info(("    Updating %s: (%s + %s) > %s" if modifyAllowed else
                         "    %s needs updating: (%s + %s) > %s") \
                         % (hz, hz, tn, newSortString))
            if modifyAllowed:
                project.ReversalSetForm(entry, newSortString, ChineseSortWS)
            UpdatedSortStrings += 1
                
        # (Subentries don't need the sort string)

    ChineseWS,\
    ChineseTonenumWS,\
    ChineseSortWS = ChineseWritingSystems(project, report, Hanzi=True, Tonenum=True, Sort=True)

    if not ChineseWS or not ChineseTonenumWS or not ChineseSortWS:
        report.Error("Please read the instructions and configure the necessary writing systems")
        return
    else:
        report.Info("Using writing systems:")
        report.Info("    Hanzi: %s" % project.WSUIName(ChineseWS))
        report.Info("    Tone number Pinyin: %s" % project.WSUIName(ChineseTonenumWS))
        report.Info("    Chinese sort field: %s" % project.WSUIName(ChineseSortWS))

    SortDB = SortStringDB()

    index = project.ReversalIndex(ChineseWS)
    if index:
        report.ProgressStart(index.AllEntries.Count)
        report.Info("Updating sort strings for '%s' reversal index"
                    % project.WSUIName(ChineseWS))
        for entryNumber, entry in enumerate(project.ReversalEntries(ChineseWS)):
            report.ProgressUpdate(entryNumber)
            __WriteSortString(project, entry)
    
    report.Info(("  %d %s updated" if modifyAllowed else
                 "  %d %s to update") \
                 % (UpdatedSortStrings, "entry" if (UpdatedSortStrings==1) else "entries"))

#----------------------------------------------------------------

FlexToolsModule = FlexToolsModuleClass(runFunction = UpdateReversalSortFields,
                                       docs = docs)
            

#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
