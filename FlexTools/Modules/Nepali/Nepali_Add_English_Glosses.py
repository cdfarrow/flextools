# -*- coding: utf-8 -*-
#
#   Nepali.Add_English_Glosses
#    - A FlexTools Module
#
#   Scans a FLEx database looking up the Nepali glosses in a Nepali-English
#   dictionary and populating the English field if a gloss is found.
#   Note: will not overwrite the English field if there is data in it.
#
#
# Dan McCloy & Craig Farrow
# June 2012
#
# Platforms: Python .NET
#

from FTModuleClass import *

import sys
import os
import re
from types import *

#----------------------------------------------------------------
# Configurables:

# File containing mapping of Nepali to English
glossFile = os.path.join(os.path.dirname(__file__), 'nep_en_gloss.txt')

sourceLanguage = 'ne'
targetLanguage = 'en'

TestNumberOfEntries  = -1   # -1 for whole DB; else no. of db entries to scan

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Add English Gloss",
        FTM_Version    : 1,
        FTM_ModifiesDB : True,
        FTM_Synopsis   : "Generate English gloss from the Nepali gloss.",
        FTM_Help       : None,
        FTM_Description:
u"""
Looks up the Nepali glosses in a Nepali-English
dictionary and populates the English field if a gloss is found.

Note: will not overwrite the English field if there is data in it.
""" }


import codecs
import re

def devEssence(s):
    """Given a Devanagari input string (Unicode), returns a simplified form
    in which phonologically insignificant differences are standardized."""
    s = re.sub(u'इ', u'ई', s)
    s = re.sub(u'उ', u'ऊ', s)
    s = re.sub(u'ि', u'ी', s)
    s = re.sub(u'ु', u'ू', s)
    s = re.sub(u'श', u'स', s)
    s = re.sub(u'ष', u'स', s)
    s = re.sub(ur'[- \u200C\u200D]', '', s)
    return s

def loadGlossDictionary():
    # Read glosses file
    f = codecs.open(glossFile, encoding='utf-8')
    global geDict
    geDict = dict()
    for line in f:
        m = re.search(r'(.+)\t(.+)', line)
        if (m):
            ge = m.group(2)
            de = devEssence(m.group(1))
            if de in geDict:
                geDict[de] += " / " + ge
            else:
                geDict[de] = ge
    #print "Loaded", len(geDict), "glosses...\n"
    f.close()




#----------------------------------------------------------------
# The main processing function

def NepaliToEnglishGloss(DB, report, modifyAllowed):
    """
    This is the main processing function.
    """

    if not DB.WSUIName(sourceLanguage):
        report.Error("Nepali ('%s') writing system not found in this project!" \
                        % sourceLanguage)
        return
    
    loadGlossDictionary()

    report.Info("%d entries loaded from gloss dictionary" % len(geDict))

    limit = TestNumberOfEntries

    if limit > 0:
        report.Warning("TEST: Scanning first %i entries..." % limit)
    else:
        report.Info("Scanning %i entries..." % DB.LexiconNumberOfEntries())

    addedCount = 0
  
    for e in DB.LexiconAllEntries():
        # lexeme = DB.LexiconGetLexemeForm(e)
        for sense in e.SensesOS:
            sourceGloss = DB.LexiconGetSenseDefinition(sense, sourceLanguage)
            if not sourceGloss: continue
            report.Info (sourceGloss)
            targetGloss = DB.LexiconGetSenseGloss(sense, targetLanguage)
            if not targetGloss:
                sourceGloss = devEssence(sourceGloss)
                try:
                    targetGloss = geDict[sourceGloss]
                except:
                    # not found
                    continue
                report.Info("Setting gloss to '%s'" % targetGloss)
                addedCount += 1
                if modifyAllowed:
                    DB.LexiconSetSenseGloss(sense, targetGloss, targetLanguage)
                         
        if limit > 0:
           limit -= 1
        elif limit == 0:
           break

    if modifyAllowed:
        report.Info("Matched and inserted %d glosses." % addedCount)
    else:
        report.Info("Matched %d glosses." % addedCount)

#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:

FlexToolsModule = FlexToolsModuleClass(runFunction = NepaliToEnglishGloss,
                                       docs = docs)

#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
