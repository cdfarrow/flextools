# -*- coding: utf-8 -*-
#
#   Duplicates.Merge Senses
#    - A FlexTools Module
#
#   Merges duplicate senses.
#
#   C D Farrow
#   June 2014
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

docs = {FTM_Name       : "Merge Senses",
        FTM_Version    : 1,
        FTM_ModifiesDB : True,
        FTM_Synopsis   : "Merges senses with matching gloss/definition and grammatical category.",
        FTM_Help       : "Merging Duplicates Help.htm",
        FTM_Description:
u"""
Scans all lexical entries and merges all top-level senses that have the same
grammatical category and the same gloss (or definition if the gloss field is empty).
Later senses are merged into earlier matching ones. Glosses, definitions, semantic domains,
etc. are appended if they are different.

If database modification is permitted, then the commands are actioned, otherwise
this module just reports duplicate senses.

WARNING: Always back-up the project first, and then carefully review the results
to be sure there were no mistakes or unintended effects.
""" }


#----------------------------------------------------------------

def MergeSenses(DB, report, modifyAllowed):

    numEntries = DB.LexiconNumberOfEntries()
    report.Info(u"Scanning %s entries for duplicate senses..." % numEntries)
    report.ProgressStart(numEntries)

    DoMerge = AddTagToField = modifyAllowed

    tagsField = DB.LexiconGetEntryCustomFieldNamed(u"FTFlags")
    if not tagsField:
        report.Warning(u"FTFlags custom field doesn't exist at entry level")
    elif not DB.LexiconFieldIsStringType(tagsField):
        report.Warning(u"FTFlags custom field is not of type Single-line Text")
        tagsField = None
    if AddTagToField and not tagsField:
        report.Warning(u"Continuing without writing to FTFlags")
        AddTagToField = False


    totalEntries = 0
    totalMerged  = 0

    for entryNumber, entry in enumerate(DB.LexiconAllEntries()):
        report.ProgressUpdate(entryNumber)

        mergeList = defaultdict(list)

        # Collate matching senses
        for sense in entry.SensesOS:
            if not sense.MorphoSyntaxAnalysisRA:    # Sometimes MSA is missing
                continue

            # Match on gloss/definition and POS
            #   sense.ShortName defaults to best gloss and falls back to best definition.
            #   MSA.InterlinearName is concise and more specific than MSA.LongName
            key = u"{} [{}]".format(sense.ShortName,
                                    sense.MorphoSyntaxAnalysisRA.InterlinearName)
            mergeList[key].append(sense)

        # Merge the duplicates
        merged = False
        for key, senses in mergeList.items():
            if len(senses) > 1:
                if not DoMerge:
                    msg = u"   %s [%s]: senses %s to be merged"
                else:
                    msg = u"   Merging %s [%s]: senses %s"

                senseNumbers = u" & ".join([u", ".join([s.SenseNumber for s in senses[:-1]]),
                                            senses[-1].SenseNumber])
                report.Info(msg % (entry.HomographForm,
                                   senses[0].ShortName,
                                   senseNumbers),
                            DB.BuildGotoURL(entry))

                if DoMerge:
                    originalNumSenses = entry.SensesOS.Count
                    # Merge (collapsing Last into previous, etc.)
                    senses.reverse()
                    for source, target in zip(senses, senses[1:]):
                        target.MergeObject(source, True) # Append conflicting data
                        totalMerged += 1

                    # A simple check in case we hit a corner case where something goes wrong.
                    if originalNumSenses - (len(senses)-1) <> entry.SensesOS.Count:
                        report.Warning(u"%s: Error merging senses--%i senses -%i senses <> %i" %
                                       entry.HomographForm,
                                       originalNumSenses,
                                       len(senses)-1,
                                       entry.SensesOS.Count)
                    merged = True

        if merged:
            totalEntries += 1
            if AddTagToField:
                DB.LexiconAddTagToField(entry, tagsField, TAG_MergedSenses) 
            
    if DoMerge:
        report.Info(u"%i %s merged (in %i %s)" %
                    (totalMerged, u"sense" if totalMerged == 1 else u"senses",
                     totalEntries, u"entry" if totalEntries == 1 else u"entries"))

        
#----------------------------------------------------------------

FlexToolsModule = FlexToolsModuleClass(runFunction = MergeSenses,
                                       docs = docs)

#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
