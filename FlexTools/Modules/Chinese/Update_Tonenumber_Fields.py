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

from flextoolslib import *

import site
site.addsitedir(r"Lib")

from ChineseUtilities import ChineseWritingSystems, ChineseParser


#----------------------------------------------------------------
# Documentation for the user:

docs = {FTM_Name       : "Update Tone Number Fields",
        FTM_Version    : "4.0",
        FTM_ModifiesDB : True,
        FTM_Synopsis   : "Generate Pinyin with tone numbers from Chinese Hanzi",
        FTM_Help       : r"Doc\Chinese Utilities Help.pdf",
        FTM_Description:
"""
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

                 
#----------------------------------------------------------------
# The main processing function

UpdatedSenses = 0
UpdatedReversals = 0

def UpdateTonenumberFields(project, report, modifyAllowed=False):

    def __WriteSenseTonenum(project, entry, sense):
        global UpdatedSenses
        hz = project.LexiconGetSenseGloss(sense, ChineseWS)
        tn = project.LexiconGetSenseGloss(sense, ChineseTonenumWS)
        headword = project.LexiconGetHeadword(entry)

        newTonenum, msg = Parser.CalculateTonenum(hz, tn)
        if msg:
            report.Warning("    %s: %s" % (headword, msg),
                           project.BuildGotoURL(entry))
        if newTonenum is not None:
            report.Info(("    Updating %s: %s > %s" if modifyAllowed else
                         "    %s needs updating: %s > %s") \
                         % (headword, hz, newTonenum))
            if modifyAllowed:
                project.LexiconSetSenseGloss(sense, newTonenum, ChineseTonenumWS)
            UpdatedSenses += 1
                                    
        # Subentries
        for se in sense.SensesOS:
            __WriteSenseTonenum(project, entry, se)

    def __WriteReversalTonenum(project, entry):
        global UpdatedReversals
        hz = project.ReversalGetForm(entry, ChineseWS)
        tn = project.ReversalGetForm(entry, ChineseTonenumWS)
        
        newTonenum, msg = Parser.CalculateTonenum(hz, tn)
        if msg:
            report.Warning("    %s" % msg,
                           project.BuildGotoURL(entry))
        if newTonenum is not None:
            report.Info(("    Updating %s > %s" if modifyAllowed else
                         "    %s needs updating > %s") \
                         % (hz, newTonenum))
            if modifyAllowed:
                project.ReversalSetForm(entry, newTonenum, ChineseTonenumWS)
            UpdatedReversals += 1
                
        # Subentries (Changed from OC to OS in FW8)
        try:
            subentries = entry.SubentriesOC
        except AttributeError:
            subentries = entry.SubentriesOS
            
        for se in subentries:
            __WriteReversalTonenum(project, se)


    # -----------------------------------------------------------
    # Find the Chinese writing systems

    ChineseWS,\
    ChineseTonenumWS = ChineseWritingSystems(project, report, Hanzi=True, Tonenum=True)

    if not ChineseWS or not ChineseTonenumWS:
        report.Error("Please read the instructions and configure the necessary writing systems")
        return
    else:
        report.Info("Using these writing systems:")
        report.Info("    Hanzi: %s" % project.WSUIName(ChineseWS))
        report.Info("    Tone number Pinyin: %s" % project.WSUIName(ChineseTonenumWS))

    Parser = ChineseParser()
    
    # Lexicon Glosses

    report.Info("Updating tone number Pinyin for all lexical entries")
    report.ProgressStart(project.LexiconNumberOfEntries(), "Lexicon")
   
    for entryNumber, entry in enumerate(project.LexiconAllEntries()):
        report.ProgressUpdate(entryNumber)
        for sense in entry.SensesOS:
            __WriteSenseTonenum(project, entry, sense)

    report.Info(("  %d %s updated" if modifyAllowed else
                 "  %d %s to update") \
                 % (UpdatedSenses, "sense" if (UpdatedSenses==1) else "senses"))
    
    # Reversal Index
    
    index = project.ReversalIndex(ChineseWS)
    if index:
        report.ProgressStart(index.AllEntries.Count, "Reversal index")
        report.Info("Updating tone number Pinyin for '%s' reversal index"
                    % project.WSUIName(ChineseWS))
        for entryNumber, entry in enumerate(project.ReversalEntries(ChineseWS)):
            report.ProgressUpdate(entryNumber)
            __WriteReversalTonenum(project, entry)
            
    report.Info(("  %d %s updated" if modifyAllowed else
                 "  %d %s to update") \
                 % (UpdatedReversals, "entry" if (UpdatedReversals==1) else "entries"))
    
#----------------------------------------------------------------

FlexToolsModule = FlexToolsModuleClass(runFunction = UpdateTonenumberFields,
                                       docs = docs)
            

#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
