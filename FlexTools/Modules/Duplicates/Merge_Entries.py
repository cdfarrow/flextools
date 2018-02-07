# -*- coding: utf-8 -*-
#
#   Duplicates.Merge Entries
#    - A FlexTools Module
#
#   Used in conjunction with "Find Duplicate Entries"
#
#   Merges homographs or deletes entries according to the following tags
#   in FTFlags (entry level custom Single-line Text field):
#
#       ‘del’:  delete the entry
#   	‘mt’:   the merge target--all other homographs will will be merged into this entry.
#       ‘m’:    merge into the merge target with all string conflicts appended.
#       ‘md’:   merge into the merge target with all string conflicts discarded.
#
#   C D Farrow
#   May 2014
#
#   Platforms: Python.NET
#

from FTModuleClass import *

from __DuplicatesConfig import *

from collections import defaultdict
from types import *

from SIL.Utils import StringUtils
from SIL.FieldWorks.Common.COMInterfaces import ITsString, ITsStrBldr

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Merge Entries",
        FTM_Version    : 1,
        FTM_ModifiesDB : True,
        FTM_Synopsis   : "Merges homographs and deletes entries according to merge commands in FTFlags.",
        FTM_Help       : "Merging Duplicates Help.htm",
        FTM_Description:
u"""
This Module is designed to be used in conjunction with "Find Duplicate Entries",
however it can be used independently by manually configuring the merge tags in FTFlags.

Homographs are merged according to the following tags in FTFlags (entry level):

 - ‘mt’:   the merge target. All other tagged homographs will be merged into this entry.
 

 - ‘m’:    merge into the merge target with all string conflicts appended.
 

 - ‘md’:   merge into the merge target with all string conflicts discarded.

Note: If there is are no entries tagged ‘mt’ then one of the entries tagged ‘m’
will be chosen as the merge target.

Additionally, all entries tagged ‘del’ (or 'delete') will be deleted.

Note: This module does not merge duplicate senses. See the Merge Senses module.

If database modification is permitted, then the commands are actioned, otherwise
this module reports what it would do, and highlights any errors in the command tags.

WARNING: Always back-up the project first, and then carefully review the results
to be sure there were no mistakes or unintended effects.
""" }


#----------------------------------------------------------------

def MergeEntries(DB, report, modifyAllowed):

    # --------------------------------------------------------------------
    def __EntryMessage(entry, message, reportFunc=report.Info):
        POSList = u"; ".join(set([x.ShortName for x in entry.MorphoSyntaxAnalysesOC]))
        reportFunc(u"   %s [%s][%s] %s" % (entry.HomographForm,
                                           DB.BestStr(MorphType.Name),
                                           POSList,
                                           message),
                    DB.BuildGotoURL(entry))
        
    # --------------------------------------------------------------------
    def __WarningMessage(entry, message):
        __EntryMessage(entry, message, report.Warning)

   
    # --------------------------------------------------------------------
    numEntries = DB.LexiconNumberOfEntries()
    report.Info(u"Scanning %s entries for merge commands..." % numEntries)
    report.ProgressStart(numEntries)

    tagsField = DB.LexiconGetEntryCustomFieldNamed(u"FTFlags")
    if not tagsField:
        report.Error(u"FTFlags custom field doesn't exist at entry level")
    elif not DB.LexiconFieldIsStringType(tagsField):
        report.Error(u"FTFlags custom field is not of type Single-line Text")
        tagsField = None
    if not tagsField:
        report.Warning(u"Please read the instructions")
        return

    DoCommands = modifyAllowed

    # mergeList is a dictionary of dictionaries
    
    def dict_list_factory():
        return defaultdict(list)

    mergeList = defaultdict(dict_list_factory)
    deleteList = list()

    for entryNumber, entry in enumerate(DB.LexiconAllEntries()):
        report.ProgressUpdate(entryNumber)

        MorphType = entry.LexemeFormOA.MorphTypeRA
        
        tag = DB.LexiconGetFieldText(entry, tagsField)
        if not tag: continue
        tag = tag.lower()
        
        if tag.startswith(TAG_MergeDelete):
            deleteList.append(entry)

            # Usage count in the text corpus is different to the information given in
            # the deletion warning message.
            usageCount = DB.LexiconEntryAnalysesCount(entry)

            __EntryMessage(entry, u"to be deleted (used %i time%s in text corpus)" %
                                  (usageCount, u"" if usageCount == 1 else u"s"))
            
            deleteWarningMessage = ITsString(entry.DeletionTextTSS).Text
            cut = deleteWarningMessage.find(u"1.")
            if cut >= 0:
                deleteWarningMessage = deleteWarningMessage[cut:]\
                                       .replace(StringUtils.kChHardLB, "\n")
                report.Warning("%s is in use. See tooltip for more info."\
                               % entry.HomographForm,
                               deleteWarningMessage)
                                 
        elif tag in ALL_MERGE_TAGS:

            # Ignore affixes
            if MorphType.IsAffixType:
                continue

            # Handle Grammatical Categories as sets: so senses of (Noun, Verb) will match (Verb, Noun)
            POS = set([x.ShortName for x in entry.MorphoSyntaxAnalysesOC])
            POSList = u"; ".join(POS)
            
            # Record this entry for merging
            key = u"{} [{}][{}]".format(entry.HomographForm,
                                        DB.BestStr(MorphType.Name),
                                        POSList)
            mergeList[key][tag].append(entry)


    if DoCommands:
        report.Info(u"Actioning merge commands...")
    else:
        report.Info(u"Run again with 'Modify enabled' to carry out these actions:")


    # MERGE
    totalMerged = 0
    totalTarget = 0

    report.ProgressStart(len(mergeList.items()) + len(deleteList))
    progressCount = 0
    
    for key, mergeData in mergeList.items():
        progressCount += 1
        report.ProgressUpdate(progressCount)

        # Validity checks
        if len(mergeData[TAG_MergeTarget]) > 1:
            __WarningMessage(mergeData[TAG_MergeTarget][0],
                             u"Multiple merge targets: ignoring")
            continue

        if len(mergeData[TAG_MergeTarget]) == 0:
            if len(mergeData[TAG_Merge]) == 0:
                __WarningMessage(mergeData[TAG_MergeDiscard][0],
                                 u"No merge target specified: ignoring")
                continue
            
            targetEntry = mergeData[TAG_Merge].pop()
        else:
            targetEntry = mergeData[TAG_MergeTarget][0]

        merged = False
        # Do the merges
        for entry in mergeData[TAG_Merge]:
            if DoCommands:
                targetEntry.MergeObject(entry, True)    # Append data
            merged = True
            totalMerged += 1

        for entry in mergeData[TAG_MergeDiscard]:
            if DoCommands:
                targetEntry.MergeObject(entry, False)   # Discard conflicting data
            merged = True
            totalMerged += 1

        if merged:
            if DoCommands:
                DB.LexiconSetFieldText(targetEntry, tagsField, TAG_MergeComplete)
                __EntryMessage(targetEntry, "merged")
            else:
                __EntryMessage(targetEntry, "to be merged")
            totalTarget += 1
        else:
            __WarningMessage(targetEntry, u"Only one entry tagged for merging: ignoring")
            
    if DoCommands:
        report.Info(u"%i %s merged into %i merge target%s" %
                    (totalMerged, u"entry" if totalMerged == 1 else u"entries",
                     totalTarget, u"" if totalTarget == 1 else u"s"))


    # DELETE
    if DoCommands and deleteList:
        report.Info("Deleting %i entries" % len(deleteList))

        for entry in deleteList:
            entry.Delete()      # OnBeforeObjectDeleted() will fix homograph numbering

            progressCount += 1
            report.ProgressUpdate(progressCount)

    
#----------------------------------------------------------------

FlexToolsModule = FlexToolsModuleClass(runFunction = MergeEntries,
                                       docs = docs)

#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
