# -*- coding: utf-8 -*-
#
#   Duplicates.Find Duplicate Entries
#    - A FlexTools Module
#
#   Scans a FLEx project checking for homographs with the same grammatical
#   category, and tags them as candidates for merging.
#
#   If changes are enabled then the entry-level custom field FTFlags is used to 
#   record merge recommendations. The user should review these and edit as
#   necessary before using the Module "Merge Entries"
#
#   C D Farrow
#   May 2014
#
#   Platforms: Python .NET and IronPython
#

from flextools import *

from SIL.LCModel import *
from SIL.LCModel import MoMorphTypeTags

from __DuplicatesConfig import *

from collections import defaultdict
from types import *

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Find Duplicate Entries",
        FTM_Version    : 2,
        FTM_ModifiesDB : True,
        FTM_Synopsis   : "Finds potential duplicate entries and tags them ready for merging.",
        FTM_Help       : "Merging Duplicates Help.htm",
        FTM_Description:
"""
This module scans all lexical entries that have homographs, and reports on any
entries that have the same morpheme type and same grammatical info (i.e. part-of-speech).

If project modification is permitted, then "m" is written to the 
entry-level custom field called FTFlags for any entries that meet 
the criteria above. Within FieldWorks the entries can be filtered on 
FTFlags, and the value edited for use by the Merge Entries module.

If any homographs have only one in the set, then "review" is written to FTFlags.

Note: The FTFlags field must already exist and should be created as a 'Single-line text' field using the 'First Analysis Writing System.'

Note: it is recommended to run the utility "Find and fix errors in a Fieldworks data file"
(Tools | Utilities menu) before using this module. This utility will clean
up homograph numbers and duplicate grammatical info details.
""" }


#----------------------------------------------------------------
# The main processing function

def MainFunction(project, report, modifyAllowed):

    def __EntryMessage(project, entry, message):
        report.Info("   %s(%i) [%s][%s] %s" % (entry.HomographForm,
                                                entry.HomographNumber,
                                                project.BestStr(MorphType.Name),
                                                POSList,
                                                message),
                    project.BuildGotoURL(entry))

    numEntries = project.LexiconNumberOfEntries()
    report.Info("Scanning %s entries for homographs..." % numEntries)
    report.ProgressStart(numEntries)

    AddTagToField = modifyAllowed

    tagsField = project.LexiconGetEntryCustomFieldNamed("FTFlags")
    if not tagsField:
        report.Warning("FTFlags custom field doesn't exist at entry level")
    elif not project.LexiconFieldIsStringType(tagsField):
        report.Error("FTFlags custom field is not of type Single-line Text")
        tagsField = None
    if AddTagToField and not tagsField:
        report.Warning ("Continuing in read-only mode")
        AddTagToField = False
   
    homographs = defaultdict(list)

    for entryNumber, entry in enumerate(project.LexiconAllEntries()):
        if (entry.HomographNumber == 0):
            continue

        report.ProgressUpdate(entryNumber)
        
        POSList = ""
        MorphType = entry.LexemeFormOA.MorphTypeRA

        # Ignore affixes
        if MorphType.IsAffixType:
            continue

        # Ignore variants and complex forms (except phrases)
        if entry.EntryRefsOS.Count > 0:
            if ((MorphType.Guid != MoMorphTypeTags.kguidMorphPhrase) and
                (MorphType.Guid != MoMorphTypeTags.kguidMorphDiscontiguousPhrase)):
                __EntryMessage(project, entry, "skipped because it is a variant or complex form")
                continue

        # Handle Grammatical Categories as sets: so senses of (Noun, Verb) will match (Verb, Noun)
        POS = set([x.ShortName for x in entry.MorphoSyntaxAnalysesOC])
        POSList = "; ".join(POS)

        # Skip entries with contents in FTFlags
        if tagsField:
            tag = project.LexiconGetFieldText(entry, tagsField)
            if tag:
                if tag in ALL_MERGE_TAGS:
                    __EntryMessage(project, entry, "ready for merge (FTFlags = '%s')" % tag)
                else:
                    __EntryMessage(project, entry, "skipped because FTFlags contains data ('%s')" % tag)
                continue

        # Keep track of this entry
        key = "{} [{}][{}]".format(entry.HomographForm,
                                   project.BestStr(MorphType.Name),
                                   POSList)

        homographs[key].append(entry)
        __EntryMessage(project, entry, "")


    if AddTagToField:
        s = "Writing tag '%s' to FTFlags" % TAG_Merge
    else:
        s = "Run again with 'Modify enabled' to write '%s' to FTFlags" % TAG_Merge
    report.Info("Homographs to consider for merging: (%s)" % s)

    homographItems = sorted(homographs.items())
    for key, data in homographItems:
        if len(data) < 2:
            continue
        report.Info("   {}: {} homographs".format(key, len(data)),
                    project.BuildGotoURL(data[0]))
        if AddTagToField:
            for e in data:
                project.LexiconAddTagToField(e, tagsField, TAG_Merge) 

    # Mark entries with only one homograph with "review"
    
    if AddTagToField:
        s = "Writing tag '%s' to FTFlags" % TAG_MergeReview
    else:
        s = "Run again with 'Modify enabled' to write '%s' to FTFlags" % TAG_MergeReview
    report.Info("Homographs with no matching entry: (%s)" % s)
    for key, data in homographItems:
        if len(data) == 1:
            report.Info("   {}".format(key),
                        project.BuildGotoURL(data[0]))
            if AddTagToField:
                e = data[0]
                project.LexiconAddTagToField(e, tagsField, TAG_MergeReview) 

#----------------------------------------------------------------

FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)

#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
