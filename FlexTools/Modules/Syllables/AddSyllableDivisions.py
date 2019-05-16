# -*- coding: utf-8 -*-
#
#   Syllables.AddSyllableDivisions
#    - A FlexTools Module
#
#   Get pronunciation and add syllable divisions (periods) according to rules
#
#   The resulting divided pronucian is placed in the Syllables (entry-level)
#   field if changes are enabled. This allows further processing with 
#   Phonlogy Assistant
#
# G Trihus
# December 2014
#
# Platforms: Python .NET and IronPython
#

from FTModuleClass import *

from System.Xml import XmlDocument


#----------------------------------------------------------------
# Configurables:

TestNumberOfEntries  = -1   # -1 for whole DB; else no. of db entries to scan

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Syllables - Add Syllable Divisions",
        FTM_Version    : 1,
        FTM_ModifiesDB : True,
        FTM_Synopsis   : "Add Periods between syllables accoring to rules",
        FTM_Help       : None,
        FTM_Description:
u"""
This module checks creates a new field Syllables from the prounciation

If database modification is permitted, then a the resulting value will be placed
in the entry-level custom field called Syllables. This field must already exist
and should be created as a 'Single-line text' field using the 'phonetic writing
system'
""" }


#----------------------------------------------------------------
# The main processing function

def MainFunction(DB, report, modifyAllowed):
    """
    This is the main processing function.

    This example illustrates:
     - Processing over all lexical entries and their senses.
     - Adding resuls to a custom field.
     - Report messages that give feedback and information to the user.
     - Report messages that include a hyperlink to the entry (for Warning & Error only).
    
    """
    report.Info("Beginning to create syllables for Pronunciations")
    
    limit = TestNumberOfEntries

    if limit > 0:
        report.Warning("TEST: Scanning first %i entries..." % limit)
        report.ProgressStart(limit)
    else:
        numberEntries = DB.LexiconNumberOfEntries()
        report.Info("Scanning %i entries..." % numberEntries)
        report.ProgressStart(numberEntries)

    UpdateField = modifyAllowed

    syllablesField = DB.LexiconGetEntryCustomFieldNamed("Syllables")
    if UpdateField and not syllablesField:
        report.Error("Syllables custom field doesn't exist at entry level")
        UpdateField = False

    pData = XmlDocument()
    pData.Load('Modules/Syllables/PhoneticInventory.xml')

    for entryNumber, entry in enumerate(DB.LexiconAllEntries()):
        report.ProgressUpdate(entryNumber)
        lexeme = DB.LexiconGetLexemeForm(entry)
        for pronunciation in entry.PronunciationsOS:
            if DB.LexiconGetPronunciation(pronunciation) == None:
                report.Warning("Blank pronunciation: " + lexeme, DB.BuildGotoURL(entry))
                continue
            if syllablesField:
                curPronunciation = DB.LexiconGetFieldText(entry, syllablesField)
            else:
                curPronunciation = None
            if curPronunciation == None:
                curPronunciation = DB.LexiconGetPronunciation(pronunciation)
            result = Convert(curPronunciation, pData, report, lexeme)
            report.Warning(lexeme + ": " + curPronunciation + " -> " + result, DB.BuildGotoURL(entry))
            if UpdateField:
               DB.LexiconSetFieldText(entry, syllablesField, result)
           
        if limit > 0:
           limit -= 1
        if limit == 0:
           break

#----------------------------------------------------------------
# Convert was designed for Encoding Converters / Bulk Edit to do the work

def Convert(bytesInput, pData, report, lexeme):
    if '.' in bytesInput:
        return bytesInput
    pat = u''
    pos = 0
    posList = []
    skip = False
    for c in bytesInput:
        symdef = pData.SelectSingleNode('//symbolDefinition[@literal="' + c + '"]/type')
        if symdef == None:
            report.Warning(lexeme + ": " + bytesInput + ": " + c + " not found")
            pos += 1
            continue
        pc = symdef.InnerText[:1].upper()
        if pc in "CV":
            if skip:
                skip = False
            else:
                pat += pc
                posList.append(pos)
        elif c in u"\u0361\u035c":
            skip = True
        pos += 1
    ilen = len(pat);
##    report.Info(pat + ": " + repr(posList) + "/ " + repr(bytesInput))
    pats = ['CCVC', 'CCV', 'CVC', 'CV', 'VC', 'V'] #longest to shortest
    r = u''
    while ilen > 0:
        for p in pats:
            mlen = len(p)
            if pat[-mlen:] == p:
                start = posList[ilen - mlen]
                r = u'.' + bytesInput[start:] + r
                bytesInput = bytesInput[:start]
                pat = pat[:-mlen]
                ilen -= mlen
                break
            else:
                mlen = 0
        if mlen == 0:
            report.Warning(lexeme + ": No syllable pattern match")
            mlen = 1
            start = posList[ilen - mlen]
            r = u'.' + bytesInput[start:] + r
            bytesInput = bytesInput[:start]
            pat = pat[:-mlen]
            ilen -= mlen
    return r[1:]

#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:

FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)

#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
