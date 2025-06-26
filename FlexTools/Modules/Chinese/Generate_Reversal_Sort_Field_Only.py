#
#   Chinese.Generate Reversal Sort Field Only
#    - A FlexTools Module -
#
#   Finds the Chinese Reversal Index and uses the Hanzi field to 
#   generate the Pinyin Numbered field, and then uses those to populate 
#   the Sort field. See documentation below for the Writing System
#   codes.
#
#   C D Farrow
#   Jul 2016
#
#   Platforms: Python .NET and IronPython
#

from flextoolslib import *

#----------------------------------------------------------------
# Documentation for the user:

docs = {FTM_Name       : "Generate Reversal Index Sort Field Only",
        FTM_Version    : "4.0",
        FTM_ModifiesDB : True,
        FTM_Synopsis   : "Generates the Chinese sort field in the Chinese Reversal Index. Sorts by pronunciation.",
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

This Module generates the Pinyin tone number field from the Hanzi
field and then generates the Sort field from those two. The sort field will be left 
blank for any entries with ambiguities in the tone number field .

The sort field produced by this Module orders Chinese by pronunciation, then
by stroke count, and finally by stroke order. This follows the ordering in
现代汉语词典 (XianDai HanYu CiDian). Thus:

 - san < sen < shan < sheng < si < song: 三 < 森 < 山 < 生 < 四 < 送

 - lu < lü < luan < lüe: 路 < 绿 < 乱 < 掠

 - (stroke count) 录 < 录音 < 路 < 路口

 - (stroke order) zhi4 with 8 strokes: 郅 < 制 < 质 < 治

See Chinese Utilities Help.pdf for detailed information on configuration and usage.
""" }

from ChineseUtilities import ChineseParser
from ChineseUtilities import SortStringDB, ChineseWritingSystems

#----------------------------------------------------------------
# Configurables:

# Ambiguous Chinese parses are common, and need to be manually resolved in
# the tone number field. However, if anyone wants to bypass the manual
# work, two levels of hacks are provided to force a sort string calculation
# even though it might produce a slightly wrong sort order:
# HACK_FIRST_WORD_NOT_AMBIGUOUS:
#       If the first word is not ambiguous for parse or pronunciation then
#       a sort string will be generated using as many characters as aren't 
#       ambiguous. These entries will sort in the right place by at least
#       the first character.
# HACK_FIRST_WORD_IGNORE_TONE:
#       Generates the sort string for the above, AND if the pronunciation
#       matches, but the tone doesn't. These entries will sort in the right 
#       place by the first character, although they might be in the wrong
#       place by tone.
# Note: all sort strings that are hacked like this will have '(...)' appended.

HACK_NONE = 0
HACK_FIRST_WORD_NOT_AMBIGUOUS = 1
HACK_FIRST_WORD_IGNORE_TONE = 2
                 
HACK_LEVEL = 0


#----------------------------------------------------------------
import chin_utils
from os.path import commonprefix

HACK_ENDING = "()"
HACK_FULLWIDTH_ENDING = "\N{FULLWIDTH LEFT PARENTHESIS}\N{FULLWIDTH RIGHT PARENTHESIS}"                 


def HACK_Tonenum (hz, tn):
    
    def __trim_ambiguities(s):
        words = s.split()
        i = 0
        for w in words:
            if "|" in w: break
            i += 1
        return " ".join(words[:i])
        
    hacked_tn = None
    if "|" in tn: # Hack away...
        parses = tn.lower().split(" | ")
        # 2 cases: 
        if len(parses) > 1: # ambiguous parse
            #print("    Ambiguous parse:")
            parses = map(__trim_ambiguities, parses)
            parses = map(chin_utils.get_tone_syls, parses)
            longest = commonprefix(parses)
            hacked_tn = " ".join(longest)
        else:               # single parse
            #print("    Single parse")
            words = tn.split()
            firstword = words[0]
            if "|" in firstword:    # ambiguous word
                #print("    First word ambiguous:", firstword)
                if HACK_LEVEL == HACK_FIRST_WORD_IGNORE_TONE:
                    segments = firstword.split("|")
                    stripped_segs = []
                    for seg in segments:
                        stripped = [syl.rstrip("12345") for syl in chin_utils.get_tone_syls(seg.lower())]
                        stripped_segs.append("".join(stripped))
                    if len(set(stripped_segs)) == 1:    # All pronunciations the same
                        hacked_tn = segments[0]         # Arbitrarily use the first option
                    #else - different pronunciations: no hack
                #else - ambiguous first word: no hack
            else:
                # firstword not ambiguous - grab longest unambiguous sequence
                #print("    First word not ambiguous:", words)
                hacked_tn = __trim_ambiguities(tn)

    if hacked_tn:
        #print(" >>", hacked_tn)
        syls = chin_utils.get_tone_syls(hacked_tn)
        # Trim hz to match tonenum length
        hz = "".join(chin_utils.get_chars(hz)[:len(syls)])
        # Mark hacked entries
        tn = hacked_tn + HACK_ENDING 
        hz = hz + HACK_FULLWIDTH_ENDING
        
    return hz, tn

#----------------------------------------------------------------
# The main processing function

UpdatedTonenums = 0
UpdatedSortStrings = 0
HackedSortStrings = 0

def GenerateReversalSortFields(project, report, modifyAllowed=False):

    def __WriteReversalTonenumAndSortString(entry):
        global UpdatedTonenums
        global UpdatedSortStrings
        global HackedSortStrings
        
        hz = project.ReversalGetForm(entry, ChineseWS)
        tn = project.ReversalGetForm(entry, ChineseTonenumWS)
        ss = project.ReversalGetForm(entry, ChineseSortWS)
        
        # Tone number
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
            UpdatedTonenums += 1
            tn = newTonenum
                
        if HACK_LEVEL:
            hacked_hz, hacked_tn = HACK_Tonenum(hz, tn)
            if tn != hacked_tn:
                HackedSortStrings += 1
                report.Warning("    Hacked %s" % hz,
                               project.BuildGotoURL(entry))
                hz = hacked_hz
                tn = hacked_tn


        # Sort string
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

    Parser = ChineseParser()       
    SortDB = SortStringDB()

    index = project.ReversalIndex(ChineseWS)
    if index:
        report.ProgressStart(index.AllEntries.Count)
        report.Info("Updating sort strings for '%s' reversal index"
                    % project.WSUIName(ChineseWS))
        for entryNumber, entry in enumerate(project.ReversalEntries(ChineseWS)):
            report.ProgressUpdate(entryNumber)
            __WriteReversalTonenumAndSortString(entry)
    
    report.Info(("  %d %s updated" if modifyAllowed else
                 "  %d %s to update") \
                 % (UpdatedTonenums, "tone number" if (UpdatedTonenums==1) else "tone numbers"))
                 
    report.Info(("  %d %s updated" if modifyAllowed else
                 "  %d %s to update") \
                 % (UpdatedSortStrings, "sort string" if (UpdatedSortStrings==1) else "sort strings"))
    if HACK_LEVEL:
        report.Info("  %d %s hacked" \
                 % (HackedSortStrings, "sort string" if (HackedSortStrings==1) else "sort strings"))

#----------------------------------------------------------------

FlexToolsModule = FlexToolsModuleClass(runFunction = GenerateReversalSortFields,
                                       docs = docs)
            

#----------------------------------------------------------------
if __name__ == '__main__':
    print(FlexToolsModule.Help())
