#
#   Restructure Data.Convert_custom_plurals_to_variants
#    - A FlexTools Module
#
#   Convert the data in custom fields named "Plural" into variants of type Plural.
#
#   For each entry in the database, check for non-empty contents of a custom field
#   named "Plural".  If found, and if there is not already a variant with that same
#   vernacular information, create a new variant, copy the text into the Variant
#   Form field, and assign a Variant Type of "Plural". If successful, delete the
#   contents of the custom field.
#
#   Jeff Heath
#   February 2023
#
#   Platforms: Python.NET
#

from flextoolslib import *

from SIL.LCModel import *
from SIL.LCModel.Core.KernelInterfaces import ITsString, ITsStrBldr
from SIL.LCModel.Core.Text import TsStringUtils
from SIL.LCModel.Core.Cellar import CellarPropertyType

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Convert Custom Plurals",
        FTM_Version    : 2,
        FTM_ModifiesDB : True,
        FTM_Synopsis   : "Convert the data in custom fields named 'Plural' into variants of type Plural.",
        FTM_Help       : None,
        FTM_Description:
"""
This module is designed to convert custom plural fields into variants of type plural.

For each entry in the database, check for non-empty contents of a custom field
named "Plural". If found, create a new variant (if a variant with that same
vernacular text doesn't already exist), copy the text into the Variant Form field,
and assign a Variant Type of "Plural". If successful, or if the the variant
already exists, delete the contents of the custom field.

If project modification is permitted, then the commands are actioned, otherwise
this module reports what it would do.

WARNING: Always back-up the project first, and then carefully review the results
to be sure there were no mistakes or unintended effects.
""" }


#----------------------------------------------------------------

def ConvertPlurals(project, report, modifyAllowed):

    def ClearMultiString(mua):
        """
        Clears all of the strings in a MultiString.
        Applies to FieldType valus in FLExLCM.CellarUnicodeTypes
        Can be used to clear out a MultiUnicode custom field
        
        mua = MultiUnicodeAccessor for the field, e.g.
              project.project.DomainDataByFlid.get_MultiStringProp(hvo, pluralCustomFieldID)
        """

        #if not mua: raise FP_NullParameterError()

        for ws in project.GetAllVernacularWSs():
            mua.set_String(project.WSHandle(ws), None)
                    

    # --------------------------------------------------------------------
    def __EntryMessage(entry, message, reportFunc=report.Info):
        POSList = "; ".join(set([x.ShortName for x in entry.MorphoSyntaxAnalysesOC]))
        reportFunc("   %s [%s][%s] %s" % (entry.HomographForm,
                                           project.BestStr(MorphType.Name),
                                           POSList,
                                           message),
                    project.BuildGotoURL(entry))
        
    # --------------------------------------------------------------------
    def __WarningMessage(entry, message):
        __EntryMessage(entry, message, report.Warning)


    # --------------------------------------------------------------------
    numEntries = project.LexiconNumberOfEntries()
    report.Info(f"Scanning {numEntries} entries for plural conversions...")
    report.ProgressStart(numEntries)

    pluralCustomFieldID = project.LexiconGetEntryCustomFieldNamed("Plural")
    if not pluralCustomFieldID:
        report.Error("Plural custom field doesn't exist at entry level")
    else:
        if not project.LexiconFieldIsAnyStringType(pluralCustomFieldID):
            # not a field type we can handle
            report.Error("Plural custom field is not a field type we can handle")
            pluralCustomFieldID = None
    if not pluralCustomFieldID:
        report.Warning("Please read the instructions")
        return
    
    # get the main vernacular writing system handle
    vernWSHandle = project.lp.DefaultVernacularWritingSystem.Handle
    enWSHandle = project.WSHandle('en')
    
    # find and store the plural variant type
    for theType in project.ObjectsIn(ILexEntryTypeRepository):
        if theType.Name.get_String(enWSHandle).ToString() == "Plural":
            pluralVariantType = theType
            break
    
    DoCommands = modifyAllowed
    
    
    numPlurals = 0
    
    # make a pass through entries to find custom plural fields and convert to plural variants (if they don't already exist)
    for entryNumber, entry in enumerate(project.LexiconAllEntries()):
        report.ProgressUpdate(entryNumber)
        
        # Ignore affixes
        MorphType = entry.LexemeFormOA.MorphTypeRA
        if MorphType.IsAffixType:
            continue
        
        pluralStr = project.LexiconGetFieldText(entry, 
                                                pluralCustomFieldID,
                                                vernWSHandle)
        if not pluralStr or pluralStr == "***":
            # no plural field found in this entry, go to next loop iteration
            continue
        
        report.Info("\\lx {} has custom plural field {}".format(
                        project.LexiconGetLexemeForm(entry), pluralStr))
        numPlurals += 1
        
        # default action (along with removing custom plural form) is 
        # to add a plural variant
        addPluralVariant = True
        # but see if there is already a plural variant
        for theVariant in entry.VariantFormEntries.GetEnumerator():
            theVariantLexeme = project.LexiconGetLexemeForm(theVariant)
            if theVariantLexeme == pluralStr:
                # there is a match, so just remove this custom plural form
                report.Info("There is already a variant with that plural, just clear the custom field")
                addPluralVariant = False
        
        # create a new variant from the data in the plural custom field
        if project.LexiconFieldIsStringType(pluralCustomFieldID):
            # the plural type is a simple string
            # create a TsString with the plural form
            tssVariantLexemeForm = TsStringUtils.MakeString(pluralStr,
                                                            vernWSHandle)
            if DoCommands:
                if addPluralVariant:
                    # create plural variant for this entry
                    variantEntryRef = entry.CreateVariantEntryAndBackRef(
                                pluralVariantType, tssVariantLexemeForm)
                    __EntryMessage(entry, "Created plural variant {} connected to entry {}".format(tssVariantLexemeForm.ToString(), entry))
                # clear out the custom field
                project.LexiconClearField(entry, pluralCustomFieldID)
                __EntryMessage(entry, "Cleared out plural custom field")
            else:
                if addPluralVariant:
                    __EntryMessage(entry, "Plural variant {} connected to entry {} to be created".format(tssVariantLexemeForm.ToString(), entry))
                __EntryMessage(entry, "Plural custom field to be cleared out")
        else:
            # the plural type must be a Multi string
            if DoCommands:
                if addPluralVariant:
                    # create (empty) plural variant for this entry
                    variantEntryRef = entry.CreateVariantEntryAndBackRef(pluralVariantType)
                    # copy the plural field over to the variant form
                    pluralMUA = project.project.DomainDataByFlid.get_MultiStringProp(entry.Hvo, pluralCustomFieldID)
                    variantEntryRef.Owner.LexemeFormOA.Form.MergeAlternatives(pluralMUA)
                    __EntryMessage(entry, f"Created plural variant {pluralStr} connected to entry {entry}")
                # clear out the data in the custom field
                project.LexiconClearField(entry, pluralCustomFieldID)
                __EntryMessage(entry, "Cleared out plural custom field")
            else:
                if addPluralVariant:
                    __EntryMessage(entry, f"Plural variant {pluralStr} connected to entry {entry} to be created")
                __EntryMessage(entry, "Plural custom field to be cleared out")
            
        
        # if this "break" line is uncommented, only process one plural
        #break
        # if this section is uncommented, only process that number of plurals
        #if numPlurals >= 5:
            #break
    
    # give a final report
    if DoCommands:
        report.Info(f"Plural conversions made (and custom fields cleared) on {numPlurals} entries.")
    else:
        report.Info(f"Plural conversions to be made on {numPlurals} entries.")
        


#----------------------------------------------------------------

FlexToolsModule = FlexToolsModuleClass(runFunction = ConvertPlurals,
                                       docs = docs)

#----------------------------------------------------------------
if __name__ == '__main__':
    print(FlexToolsModule.Help())
