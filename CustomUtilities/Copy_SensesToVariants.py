# -*- coding: cp1252 -*-

# Copy_SensesToVariants.py
#
# An EXAMPLE module that adds new Senses to variant entries
# based on the Primary Entry Reference.
#
# NOTE: This is a work-around because variant entries don't work
# properly in the interlinear in FieldWorks 5.4.1.
#
# C D Farrow
# Feb 2009
#
# Platforms: Python .NET and IronPython
#

# The Path is supplied by FlexLibs.pth in the Site-packages directory
# with a single line pointing to the FlexLibs directory (Python.NET only)
from FLExDBAccess import FLExDBAccess

from SIL.FieldWorks.FDO.Ling import LexSense, MoMorphSynAnalysis, DummyGenericMSA
from SIL.FieldWorks.FDO.Ling import MoStemMsa, MoDerivAffMsa, MoInflAffMsa, MoUnclassifiedAffixMsa 
from SIL.FieldWorks.FDO import MsaType

import re
import operator

#----------------------------------------------------------------
# Configurables:

FLExDBName           = "Sense-experiments"

TestNumberOfEntries  = -1   # -1 for whole DB; else no. of db entries to scan

#----------------------------------------------------------------


# If your data doesn't match your system encoding (in the console) then
# redirect the output to a file: this will make it utf-8.
## BUT This doesn't work in IronPython!!
import codecs
import sys
if sys.stdout.encoding == None:
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout)
       

#-----------------------------------------------------------

# Type and Class mapping for creating new MorphoSyntaxAnalysis objects.
Map_MsaTypeToMsaClass = {
    MsaType.kRoot           : MoStemMsa, #\ Single class
    MsaType.kStem           : MoStemMsa, #/ for these two.
    MsaType.kDeriv          : MoDerivAffMsa,
    MsaType.kInfl           : MoInflAffMsa,
    MsaType.kUnclassified   : MoUnclassifiedAffixMsa }

        
#-----------------------------------------------------------

def LexiconEntryAddMSA(entry, sourceMSA):
    """
    Add a MorphoSyntaxAnalysis to the given entry from an
    existing MSA.
    # Ken Zook: Feb 2009
    # "The MorphoSyntaxInfo object that actually refers to the
    # part of speech is owned by the entry, and the sense
    # points to this object."
    (For a work-around until the next version fixes handling
    of variant entries in the interlinear. So, this function
    isn't added to FLExDBAccess at this stage.)
    """
    
    # Build a new MSA for this entry.
    dummyMSA = DummyGenericMSA.Create(sourceMSA)
    
    # Add to Entry if not already there.
    # (Based on MoClasses.cs/MoMorphSynAnalysis.UpdateOrReplace)
    # Check if it exists.
    lexMSA = None
    ##print " Entry's MSA count:", entry.MorphoSyntaxAnalysesOC.Count
    for msa in e.MorphoSyntaxAnalysesOC:
        if msa.EqualsMsa(dummyMSA):
            lexMSA = msa
            print " Found matching MSA - don't need to add new one."
            print "  >", lexMSA.ShortName, lexMSA.PartOfSpeechRAHvo
            break
    if lexMSA == None:
        print " Creating new MSA"
        lexMSA = Map_MsaTypeToMsaClass[dummyMSA.MsaType].\
                    CreateFromDummy(entry, dummyMSA)
        
        print " lexMSA:", lexMSA.ShortName, lexMSA.PartOfSpeechRAHvo
        entry.MorphoSyntaxAnalysesOC.Add(lexMSA)

    return lexMSA


# Open the database 

FlexDB = FLExDBAccess()

# No name opens the first db on the default server
if not FlexDB.OpenDatabase(FLExDBName, verbose = True):
    print "FDO Cache Create failed!"
    sys.exit(1)
       

#

limit = TestNumberOfEntries

if limit > 0: print "TEST: Scanning first", limit, "entries..."
else: print "Scanning", FlexDB.LexiconNumberOfEntries(), "entries..."

for e in FlexDB.LexiconAllEntries() :
    context = r"\lx " + FlexDB.LexiconGetLexemeForm(e)

    ## If you want to use ids instead of strings then try this:
    ##x = FlexDB.db.GetIdFromGuid(FlexDB.lp.kguidLexTypSpellingVar)
    ##print x
    if e.EntryTypeRA.ToString() == "Spelling Variant":
        print context
        for mainEntry in e.MainEntriesOrSensesRS:
            print "REF>", FlexDB.LexiconGetLexemeForm(mainEntry)

            for senseToCopy in mainEntry.SensesOS:

                print "Appending sense:", senseToCopy.Gloss
                newSense = LexSense()
                e.SensesOS.Append(newSense) # Must link in before anything else.

                # Gloss: Copy all WS values to new sense
                newSense.Gloss.CopyAlternatives(senseToCopy.Gloss)

                # Add the MorphoSyntaxAnalysis (i.e. POS) to this entry
                lexMSA = LexiconEntryAddMSA(e,
                                    senseToCopy.MorphoSyntaxAnalysisRA)

                # Link to the MSA from this sense
                newSense.MorphoSyntaxAnalysisRA = lexMSA

                # Mark the duplicated data
                newSense.Source.Text = "(Python) Copied from "+FlexDB.LexiconGetLexemeForm(mainEntry)
                

    if limit > 0:
        limit -= 1
    elif limit == 0:
        break
