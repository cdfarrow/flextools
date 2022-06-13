# -*- coding: utf-8 -*-
#
#   Chinese.Update Pinyin Fields
#    - A FlexTools Module -
#
#
#   C D Farrow
#   June 2011
#
#   Platforms: Python .NET and IronPython
#

from __future__ import unicode_literals
from builtins import str

import unicodedata

from FTModuleClass import *

import site
site.addsitedir(r"Lib")

from ChineseUtilities import ChineseWritingSystems, TonenumberToPinyin

#----------------------------------------------------------------
# Documentation for the user:

docs = {FTM_Name       : "Update Pinyin Fields",
        FTM_Version    : "4.0",
        FTM_ModifiesDB : True,
        FTM_Synopsis   : "Generate Pinyin with tone diacritics from the tone numbers",
        FTM_Help       : r"Doc\Chinese Utilities Help.pdf",
        FTM_Description:
"""
Populates the Pinyin (zh-CN-x-py) writing system
from the Pinyin Numbered (zh-CN-x-pyn) field for:

 - all glosses in the lexicon,

 - forms in a Reversal Index based on the 'zh-CN' writing system.

If the tone number has any unresolved ambiguities then the Pinyin field is
cleared, otherwise the Pinyin field is always overwritten (when database
changes are enabled.)

See Chinese Utilities Help.pdf for detailed information on configuration and usage.
""" }
                 
#----------------------------------------------------------------
# The main processing function

UpdatedSenses = 0
UpdatedReversals = 0

def UpdatePinyinFields(project, report, modifyAllowed=False):

    def __CalcNewPinyin(project, tonenum, pinyin):
        # Note that project is passed to each of these local functions otherwise
        # project is treated as a global and isn't released for garbage collection.
        # That keeps the database locked so FT has to be restarted to use
        # that database again.
        # Returns a tuple: (newPinyin, msg)
        #   newPinyin: new value for the Pinyin field
        #   msg: a warning message about the data, or None

        msg = None
        if tonenum:
            if '|' in tonenum or '[' in tonenum: 
                msg = "Ambiguous tone number: %s" % tonenum
                # Clear the Pinyin field if ambiguity in 
                # the tonenum field hasn't been resolved
                newPinyin = ""
            else:
                newPinyin = TonenumberToPinyin(tonenum)
        else:
            newPinyin = ""              # Clear if the tonenum is blank
                
        return (unicodedata.normalize('NFD', newPinyin), msg)

    def __WriteSensePinyin(project, sense, entry):
        global UpdatedSenses
        tonenum = project.LexiconGetSenseGloss(sense, ChineseTonenumWS)
        pinyin  = project.LexiconGetSenseGloss(sense, ChinesePinyinWS)
        headword = project.LexiconGetHeadword(entry)

        newPinyin, msg = __CalcNewPinyin(project, tonenum, pinyin)
        if msg:
            report.Warning("    %s: %s" % (headword, msg),
                           project.BuildGotoURL(entry))
        if newPinyin != pinyin:
            report.Info(("    Updating '%s': %s > %s" if modifyAllowed else
                         "    '%s' needs updating: %s > %s") \
                         % (headword, tonenum, newPinyin))
            if modifyAllowed:
                project.LexiconSetSenseGloss(sense, newPinyin, ChinesePinyinWS)
            UpdatedSenses += 1

        # Subentries
        for se in sense.SensesOS:
            __WriteSensePinyin(project, se, entry)

    def __WriteReversalPinyin(project, entry):
        global UpdatedReversals
        tonenum = project.ReversalGetForm(entry, ChineseTonenumWS)
        pinyin  = project.ReversalGetForm(entry, ChinesePinyinWS)
        reversalForm  = project.ReversalGetForm(entry, ChineseWS)

        newPinyin, msg = __CalcNewPinyin(project, tonenum, pinyin)
        if msg:
            report.Warning("    %s: %s" % (reversalForm, msg),
                           project.BuildGotoURL(entry))
        if newPinyin != pinyin:
            report.Info(("    Updating '%s': %s > %s" if modifyAllowed else
                         "    '%s' needs updating: %s > %s") \
                         % (reversalForm, tonenum, newPinyin))
            if modifyAllowed:
                project.ReversalSetForm(entry, newPinyin, ChinesePinyinWS)
            UpdatedReversals += 1

        # Subentries (Changed from OC to OS in FW8)
        try:
            subentries = entry.SubentriesOS
        except AttributeError:
            subentries = entry.SubentriesOC
            
        for se in subentries:
            __WriteReversalPinyin(project, se)


    # Find the Chinese writing systems

    ChineseWS,\
    ChineseTonenumWS,\
    ChinesePinyinWS = ChineseWritingSystems(project, report, Hanzi=True, Tonenum=True, Pinyin=True)

    if not ChineseTonenumWS or not ChinesePinyinWS:
        report.Error("Please read the instructions and configure the necessary writing systems")
        return
    else:
        report.Info("Using these writing systems:")
        report.Info("    Tone number Pinyin: %s" % project.WSUIName(ChineseTonenumWS))
        report.Info("    Chinese Pinyin field: %s" % project.WSUIName(ChinesePinyinWS))
   
    # Lexicon Glosses

    report.Info("Updating Pinyin for all lexical entries")
    report.ProgressStart(project.LexiconNumberOfEntries(), "Lexicon")

    for entryNumber, entry in enumerate(project.LexiconAllEntries()):
        report.ProgressUpdate(entryNumber)
        for sense in entry.SensesOS:
            __WriteSensePinyin(project, sense, entry)

    report.Info(("  %d %s updated" if modifyAllowed else
                 "  %d %s to update") \
                 % (UpdatedSenses, "sense" if (UpdatedSenses==1) else "senses"))
    
    # Reversal Index

    if ChineseWS:
        index = project.ReversalIndex(ChineseWS)
        if index:
            report.ProgressStart(index.AllEntries.Count, "Reversal index")
            report.Info("Updating Pinyin for '%s' reversal index"
                        % project.WSUIName(ChineseWS))
            for entryNumber, entry in enumerate(project.ReversalEntries(ChineseWS)):
                report.ProgressUpdate(entryNumber)
                __WriteReversalPinyin(project, entry)
                
    report.Info(("  %d %s updated" if modifyAllowed else
                 "  %d %s to update") \
                 % (UpdatedReversals, "entry" if (UpdatedReversals==1) else "entries"))


#----------------------------------------------------------------

FlexToolsModule = FlexToolsModuleClass(runFunction = UpdatePinyinFields,
                                       docs = docs)
            

#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
