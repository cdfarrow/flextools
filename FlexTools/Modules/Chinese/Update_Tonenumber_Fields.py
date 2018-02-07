# -*- coding: utf-8 -*-
#
#   Chinese.Update Tonenumber Fields
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

docs = {FTM_Name       : "Update Tone Number Fields",
        FTM_Version    : "4.0",
        FTM_ModifiesDB : True,
        FTM_Synopsis   : "Generate Pinyin with tone numbers from Chinese Hanzi",
        FTM_Help       : r"Doc\Chinese Utilities Help.pdf",
        FTM_Description:
u"""
Populates the Pinyin Numbered (zh-CN-x-pyn) writing system
from the Chinese Hanzi (zh-CN) for:

 - all glosses in the lexicon,

 - forms in a reversal Index based on the 'zh-CN' writing system.

The tone number field is produced as follows:

 - Numerals 1-5 at the end of the Pinyin pronunciation for tones 1-4 plus
 nuetral tone (5), e.g. 'hai2.zi5'

 - u-diaresis is represented with a colon (':') at the end of the syllable
 and before the tone number, e.g. lu:4se4.

Following the Pinyin formatting in 现代汉语词典 (XianDai HanYu CiDian),
the tone number field also has spaces and special
punctuation between certain syllables, e.g. 'lu4//yin1', 'jiao3.zi5'.

Ambiguities in the Pinyin are included as a list of possibilities
separated by a vertical bar '|', e.g. 'zhong1|zhong4'.

If the Pinyin is already present then it is checked
against the Chinese and any inconsistencies reported (e.g. if the Chinese has
been changed without updating the Pinyin.)

Note: So that manual edits are not lost, this Module will not over-write the Pinyin.

See Chinese Utilities Help.pdf for detailed information on configuration and usage.
""" }


from ChineseUtilities import ChineseWritingSystems, ChineseParser

                 
#----------------------------------------------------------------
# The main processing function

UpdatedSenses = 0
UpdatedReversals = 0

def UpdateTonenumberFields(DB, report, modify=False):

    def __WriteSenseTonenum(DB, entry, sense):
        global UpdatedSenses
        hz = DB.LexiconGetSenseGloss(sense, ChineseWS)
        tn = DB.LexiconGetSenseGloss(sense, ChineseTonenumWS)
        headword = DB.LexiconGetHeadword(entry)

        newTonenum, msg = Parser.CalculateTonenum(hz, tn)
        if msg:
            report.Warning("    %s: %s" % (headword, msg),
                           DB.BuildGotoURL(entry))
        if newTonenum is not None:
            report.Info(("    Updating %s: %s > %s" if modify else
                         "    %s needs updating: %s > %s") \
                         % (headword, hz, newTonenum))
            if modify:
                DB.LexiconSetSenseGloss(sense, newTonenum, ChineseTonenumWS)
            UpdatedSenses += 1
                                    
        # Subentries
        for se in sense.SensesOS:
            __WriteSenseTonenum(DB, entry, se)

    def __WriteReversalTonenum(DB, entry):
        global UpdatedReversals
        hz = DB.ReversalGetForm(entry, ChineseWS)
        tn = DB.ReversalGetForm(entry, ChineseTonenumWS)
        
        newTonenum, msg = Parser.CalculateTonenum(hz, tn)
        if msg:
            report.Warning("    %s" % msg,
                           DB.BuildGotoURL(entry))
        if newTonenum is not None:
            report.Info(("    Updating %s > %s" if modify else
                         "    %s needs updating > %s") \
                         % (hz, newTonenum))
            if modify:
                DB.ReversalSetForm(entry, newTonenum, ChineseTonenumWS)
            UpdatedReversals += 1
                
        # Subentries (Changed from OC to OS in FW8)
        try:
            subentries = entry.SubentriesOC
        except AttributeError:
            subentries = entry.SubentriesOS
            
        for se in subentries:
            __WriteReversalTonenum(DB, se)


    # -----------------------------------------------------------
    # Find the Chinese writing systems

    ChineseWS,\
    ChineseTonenumWS = ChineseWritingSystems(DB, report, Hanzi=True, Tonenum=True)

    if not ChineseWS or not ChineseTonenumWS:
        report.Error("Please read the instructions and configure the necessary writing systems")
        return
    else:
        report.Info("Using these writing systems:")
        report.Info("    Hanzi: %s" % DB.WSUIName(ChineseWS))
        report.Info("    Tone number Pinyin: %s" % DB.WSUIName(ChineseTonenumWS))

    Parser = ChineseParser()
    
    # Lexicon Glosses

    report.Info("Updating tone number Pinyin for all lexical entries")
    report.ProgressStart(DB.LexiconNumberOfEntries(), "Lexicon")
   
    for entryNumber, entry in enumerate(DB.LexiconAllEntries()):
        report.ProgressUpdate(entryNumber)
        for sense in entry.SensesOS:
            __WriteSenseTonenum(DB, entry, sense)

    report.Info(("  %d %s updated" if modify else
                 "  %d %s to update") \
                 % (UpdatedSenses, "sense" if (UpdatedSenses==1) else "senses"))
    
    # Reversal Index
    
    index = DB.ReversalIndex(ChineseWS)
    if index:
        report.ProgressStart(index.AllEntries.Count, "Reversal index")
        report.Info("Updating tone number Pinyin for '%s' reversal index"
                    % DB.WSUIName(ChineseWS))
        for entryNumber, entry in enumerate(DB.ReversalEntries(ChineseWS)):
            report.ProgressUpdate(entryNumber)
            __WriteReversalTonenum(DB, entry)
            
    report.Info(("  %d %s updated" if modify else
                 "  %d %s to update") \
                 % (UpdatedReversals, "entry" if (UpdatedReversals==1) else "entries"))
    
#----------------------------------------------------------------

FlexToolsModule = FlexToolsModuleClass(runFunction = UpdateTonenumberFields,
                                       docs = docs)
            

#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
