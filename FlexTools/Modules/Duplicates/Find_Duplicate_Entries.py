# -*- coding: utf-8 -*-
#
#   Duplicates.Find Duplicate Entries
#    - A FlexTools Module
#
#   Scans a FLEx database checking for homographs with the same grammatical category,
#   and tags them as candidates for merging.
#
#   If changes are enabled then the entry-level custom field FTFlags is used to 
#   record merge recommendations. The user should review these and edit as necessary
#   before using the Module "Merge Entries"
#
#   C D Farrow
#   May 2014
#
#   Platforms: Python .NET and IronPython
#

from FTModuleClass import *

from __DuplicatesConfig import *

from collections import defaultdict
from types import *

from SIL.FieldWorks.FDO import MoMorphTypeTags
from SIL.FieldWorks.Common.COMInterfaces import ITsString, ITsStrBldr

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Find Duplicate Entries",
        FTM_Version    : 1,
        FTM_ModifiesDB : True,
        FTM_Synopsis   : "Finds potential duplicate entries and tags them ready for merging.",
        FTM_Help       : "Merging Duplicates Help.htm",
        FTM_Description:
u"""
This Module scans all lexical entries that have homographs, and reports on any
entries that have the same morpheme type and same grammatical info (i.e. part-of-speech).

If database modification is permitted, then "m" is written to the entry-level custom
field called FTFlags for any entries that meet the criteria above. This field
must already exist and should be created as a 'Single-line text' field using the
'First Analysis Writing System.'

Note: it is recommended to run the utility "Find and fix errors in a Fieldworks data file"
(Tools | Utilities menu) before using this module. This utility will clean
up homograph numbers and duplicate grammatical info details.
""" }


#----------------------------------------------------------------
# The main processing function

def MainFunction(DB, report, modifyAllowed):

    def __EntryMessage(DB, entry, message):
        report.Info(u"   %s(%i) [%s][%s] %s" % (entry.HomographForm,
                                                entry.HomographNumber,
                                                DB.BestStr(MorphType.Name),
                                                POSList,
                                                message),
                    DB.BuildGotoURL(entry))

    numEntries = DB.LexiconNumberOfEntries()
    report.Info(u"Scanning %s entries for homographs..." % numEntries)
    report.ProgressStart(numEntries)

    AddTagToField = modifyAllowed

    tagsField = DB.LexiconGetEntryCustomFieldNamed(u"FTFlags")
    if not tagsField:
        report.Error(u"FTFlags custom field doesn't exist at entry level")
    elif not DB.LexiconFieldIsStringType(tagsField):
        report.Error(u"FTFlags custom field is not of type Single-line Text")
        tagsField = None
    if AddTagToField and not tagsField:
        report.Warning (u"Continuing in read-only mode")
        AddTagToField = False
   
    homographs = defaultdict(list)

    for entryNumber, entry in enumerate(DB.LexiconAllEntries()):
        if (entry.HomographNumber == 0):
            continue

        report.ProgressUpdate(entryNumber)
        
        POSList = u""
        MorphType = entry.LexemeFormOA.MorphTypeRA

        # Ignore affixes
        if MorphType.IsAffixType:
            continue

        # Ignore variants and complex forms (except phrases)
        if entry.EntryRefsOS.Count > 0:
            if ((MorphType.Guid <> MoMorphTypeTags.kguidMorphPhrase) and
                (MorphType.Guid <> MoMorphTypeTags.kguidMorphDiscontiguousPhrase)):
                __EntryMessage(DB, entry, u"skipped because it is a variant or complex form")
                continue

        # Handle Grammatical Categories as sets: so senses of (Noun, Verb) will match (Verb, Noun)
        POS = set([x.ShortName for x in entry.MorphoSyntaxAnalysesOC])
        POSList = u"; ".join(POS)

        # Skip entries with contents in FTFlags
        tag = DB.LexiconGetFieldText(entry, tagsField)
        if tag:
            if tag in ALL_MERGE_TAGS:
                __EntryMessage(DB, entry, u"ready for merge (FTFlags = '%s')" % tag)
            else:
                __EntryMessage(DB, entry, u"skipped because FTFlags contains data ('%s')" % tag)
            continue

        # Keep track of this entry
        key = u"{} [{}][{}]".format(entry.HomographForm,
                                   DB.BestStr(MorphType.Name),
                                   POSList)

        homographs[key].append(entry)
        __EntryMessage(DB, entry, u"")


    if AddTagToField:
        s = u"Writing tag '%s' to FTFlags" % TAG_Merge
    else:
        s = u"Run again with 'Modify enabled' to write '%s' to FTFlags" % TAG_Merge
    report.Info(u"Homographs to merge: (%s)" % s)

    homographItems = sorted(homographs.items())
    for key, data in homographItems:
        if len(data) < 2:
            continue
        report.Info(u"   {}: {} homographs".format(key, len(data)),
                    DB.BuildGotoURL(data[0]))
        if AddTagToField:
            for e in data:
                DB.LexiconAddTagToField(e, tagsField, TAG_Merge) 


    if AddTagToField:
        s = u"Writing tag '%s' to FTFlags" % TAG_MergeReview
    else:
        s = u"Run again with 'Modify enabled' to write '%s' to FTFlags" % TAG_MergeReview
    report.Info(u"Homographs with no matching entry: (%s)" % s)
    for key, data in homographItems:
        if len(data) < 2:
            report.Info(u"   {}".format(key),
                        DB.BuildGotoURL(data[0]))
            if AddTagToField:
                e = data[0]
                DB.LexiconAddTagToField(e, tagsField, TAG_MergeReview) 


#----------------------------------------------------------------

FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)

#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
