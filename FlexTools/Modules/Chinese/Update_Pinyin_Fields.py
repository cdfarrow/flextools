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

from FTModuleClass import *


#----------------------------------------------------------------
# Documentation for the user:

docs = {FTM_Name       : "Update Pinyin Fields",
        FTM_Version    : "4.0",
        FTM_ModifiesDB : True,
        FTM_Synopsis   : "Generate Pinyin with tone diacritics from the tone numbers",
        FTM_Help       : r"Doc\Chinese Utilities Help.pdf",
        FTM_Description:
u"""
Populates the Pinyin (zh-CN-x-py) writing system
from the Pinyin Numbered (zh-CN-x-pyn) field for:

 - all glosses in the lexicon,

 - forms in a Reversal Index based on the 'zh-CN' writing system.

If the tone number has any unresolved ambiguities then the Pinyin field is
cleared, otherwise the Pinyin field is always overwritten (when database
changes are enabled.)

See Chinese Utilities Help.pdf for detailed information on configuration and usage.
""" }


import unicodedata
from ChineseUtilities import ChineseWritingSystems, TonenumberToPinyin

                 
#----------------------------------------------------------------
# The main processing function

UpdatedSenses = 0
UpdatedReversals = 0

def UpdatePinyinFields(DB, report, modify=False):

    def __CalcNewPinyin(DB, tonenum, pinyin):
        # Note that DB is passed to each of these local functions otherwise
        # DB is treated as a global and isn't released for garbage collection.
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
                newPinyin = u""
            else:
                newPinyin = TonenumberToPinyin(tonenum)
        else:
            newPinyin = u""              # Clear if the tonenum is blank
                
        return (unicodedata.normalize('NFD', newPinyin), msg)

    def __WriteSensePinyin(DB, sense, entry):
        global UpdatedSenses
        tonenum = DB.LexiconGetSenseGloss(sense, ChineseTonenumWS)
        pinyin  = DB.LexiconGetSenseGloss(sense, ChinesePinyinWS)
        headword = DB.LexiconGetHeadword(entry)

        newPinyin, msg = __CalcNewPinyin(DB, tonenum, pinyin)
        if msg:
            report.Warning("    %s: %s" % (headword, msg),
                           DB.BuildGotoURL(entry))
        if newPinyin <> pinyin:
            report.Info(("    Updating '%s': %s > %s" if modify else
                         "    '%s' needs updating: %s > %s") \
                         % (headword, tonenum, newPinyin))
            if modify:
                DB.LexiconSetSenseGloss(sense, newPinyin, ChinesePinyinWS)
            UpdatedSenses += 1

        # Subentries
        for se in sense.SensesOS:
            __WriteSensePinyin(DB, se, entry)

    def __WriteReversalPinyin(DB, entry):
        global UpdatedReversals
        tonenum = DB.ReversalGetForm(entry, ChineseTonenumWS)
        pinyin  = DB.ReversalGetForm(entry, ChinesePinyinWS)
        reversalForm  = DB.ReversalGetForm(entry, ChineseWS)

        newPinyin, msg = __CalcNewPinyin(DB, tonenum, pinyin)
        if msg:
            report.Warning("    %s: %s" % (reversalForm, msg),
                           DB.BuildGotoURL(entry))
        if newPinyin <> pinyin:
            report.Info(("    Updating '%s': %s > %s" if modify else
                         "    '%s' needs updating: %s > %s") \
                         % (reversalForm, tonenum, newPinyin))
            if modify:
                DB.ReversalSetForm(entry, newPinyin, ChinesePinyinWS)
            UpdatedReversals += 1

        # Subentries (Changed from OC to OS in FW8)
        try:
            subentries = entry.SubentriesOC
        except AttributeError:
            subentries = entry.SubentriesOS
            
        for se in subentries:
            __WriteReversalPinyin(DB, se)


    # Find the Chinese writing systems

    ChineseWS,\
    ChineseTonenumWS,\
    ChinesePinyinWS = ChineseWritingSystems(DB, report, Hanzi=True, Tonenum=True, Pinyin=True)

    if not ChineseTonenumWS or not ChinesePinyinWS:
        report.Error("Please read the instructions and configure the necessary writing systems")
        return
    else:
        report.Info("Using these writing systems:")
        report.Info("    Tone number Pinyin: %s" % DB.WSUIName(ChineseTonenumWS))
        report.Info("    Chinese Pinyin field: %s" % DB.WSUIName(ChinesePinyinWS))
   
    # Lexicon Glosses

    report.Info("Updating Pinyin for all lexical entries")
    report.ProgressStart(DB.LexiconNumberOfEntries(), "Lexicon")

    for entryNumber, entry in enumerate(DB.LexiconAllEntries()):
        report.ProgressUpdate(entryNumber)
        for sense in entry.SensesOS:
            __WriteSensePinyin(DB, sense, entry)

    report.Info(("  %d %s updated" if modify else
                 "  %d %s to update") \
                 % (UpdatedSenses, "sense" if (UpdatedSenses==1) else "senses"))
    
    # Reversal Index

    if ChineseWS:
        index = DB.ReversalIndex(ChineseWS)
        if index:
            report.ProgressStart(index.AllEntries.Count, "Reversal index")
            report.Info("Updating Pinyin for '%s' reversal index"
                        % DB.WSUIName(ChineseWS))
            for entryNumber, entry in enumerate(DB.ReversalEntries(ChineseWS)):
                report.ProgressUpdate(entryNumber)
                __WriteReversalPinyin(DB, entry)
                
    report.Info(("  %d %s updated" if modify else
                 "  %d %s to update") \
                 % (UpdatedReversals, "entry" if (UpdatedReversals==1) else "entries"))


#----------------------------------------------------------------

FlexToolsModule = FlexToolsModuleClass(runFunction = UpdatePinyinFields,
                                       docs = docs)
            

#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
