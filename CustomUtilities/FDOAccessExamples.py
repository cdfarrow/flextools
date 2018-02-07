# -*- coding: cp1252 -*-

# FDOAccessExamples.py
#
# Demonstrating access to a FieldWorks project via FDO (FieldWorks Data Objects).
#
# Craig Farrow
# July 2008
#
# Platforms: Python .NET and IronPython
#
# Version 0.2: using the FLExDBAccess module. (Sep2008)
#

import site
site.addsitedir("../")

from FLExDBAccess import FLExDBAccess, FDA_DatabaseError

from SIL.FieldWorks.Common.COMInterfaces import ITsString, ITsStrBldr
from SIL.FieldWorks.Common.COMInterfaces import ISilDataAccess
# If your data doesn't match your system encoding (in the console) then
# redirect the output to a file: this will make it utf-8.
## BUT This doesn't work in IronPython!!
import codecs
import sys
if sys.stdout.encoding == None:
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout)


#============ Configurables ===============

# Database to use
dbName = "Sena 3 Experiments"

# Maximum number of entries to print out; use
# a very big number for the whole lexicon.
LexiconMaxEntries = 1

# Enable writing tests
WriteTests = False


#============ The Database ===============

FlexDB = FLExDBAccess()

try:
    FlexDB.OpenDatabase(dbName = dbName,
                        writeEnabled = WriteTests,
                        verbose = True)
except FDA_DatabaseError, e:
    print "FDO Cache Create failed!"
    print e.message
    sys.exit(1)
       

#============ The Language Project =======

# Global things in the Language Project

print "Last modified:", FlexDB.GetDateLastModified()
print

posList = FlexDB.GetPartsOfSpeech()
print len(posList), "Parts of Speech:"
for i in posList:
    print "\t", i
print


#============ Writing Systems ============

# The names of WS associated with this DB. Sorted and with no duplicates.

wsList = FlexDB.GetWritingSystems()
print len(wsList), "Writing Systems in this database: (Language Tag, Handle)"
print
for x in wsList:
    name, langTag, handle, isVern = x
    print "\t", name
    print "\t\t", langTag, handle
    print "\t\t", "(Vernacular)" if isVern else "(Analysis)"
    print ">>", FlexDB.WSUIName(langTag)
print

# A tuple of (language-tag, display-name)
print "\tDefault vernacular WS = %s; %s" % FlexDB.GetDefaultVernacularWS()
print "\tDefault analysis WS   = %s; %s" % FlexDB.GetDefaultAnalysisWS()
print

#============= Lexicon ================

print "Custom Fields:"
print "\tEntry level:"
for cf in FlexDB.LexiconGetEntryCustomFields():
    # Tuple of flid and user-defined name:
    print "\t\t%s (%s)" % (cf[1], cf[0])
print

print "\tSense level:"
for cf in FlexDB.LexiconGetSenseCustomFields():
    print "\t\t%s (%s)" % (cf[1], cf[0])
print


#--------------------------------------------------------------------
##
ftflagsFlid = FlexDB.LexiconGetSenseCustomFieldNamed("FT_Flags")
##print ftflagsFlid

#--------------------------------------------------------------------

print "Lexicon contains", FlexDB.LexiconNumberOfEntries(), "entries.",
print "( Listing up to", LexiconMaxEntries, ")"
print

# Scan the lexicon (unordered), printing some of the data
# using Standard Format markers.
# (Uses a slice to only print a portion.)
for e in list(FlexDB.LexiconAllEntries())[:LexiconMaxEntries]:
    print "\lx", FlexDB.LexiconGetLexemeForm(e)
    print "\lc", FlexDB.LexiconGetCitationForm(e)
    for sense in e.SensesOS :
        print "\ge", FlexDB.LexiconGetSenseGloss(sense)
        print "\pos", FlexDB.LexiconGetSensePOS(sense)
        print "\def", FlexDB.LexiconGetSenseDefinition(sense)
        if WriteTests and ftflagsFlid:
            flags = FlexDB.LexiconGetFieldText(sense, ftflagsFlid)
            print "FT_Flags", flags
            if flags:
                FlexDB.LexiconAddTagToField(sense, ftflagsFlid, "tag-1")
            else:
                FlexDB.LexiconSetFieldText(sense, ftflagsFlid, u"FLAG!")
            flags = FlexDB.LexiconGetFieldText(sense, ftflagsFlid)
            print "New FT_Flags", flags
        if WriteTests:
            if FlexDB.LexiconGetSenseGloss(sense) == u"Example Gloss":
                FlexDB.LexiconSetSenseGloss(sense, u"Changed Gloss")
            print "New Gloss", FlexDB.LexiconGetSenseGloss(sense)

        for example in sense.ExamplesOS:
            ex = FlexDB.LexiconGetExample(example)
            print "\ex", ex
            if WriteTests and not ex:
                # CHANGES the DB
                print "Setting example"
                FlexDB.LexiconSetExample(example,
                                         "You should have an example sentence"
                                         )

    print


#--------------------------------------------------------------------

# Alternatively:
# Create a Python dictionary of the lexicon for random access.
LexiconEntries = {}
for e in FlexDB.LexiconAllEntries():
    # Add fields of interest to 'data'
    data = {}
    data['hvo'] = e.Hvo
    glosses = []
    for sense in e.SensesOS :
        glosses.append( FlexDB.LexiconGetSenseGloss(sense))
    data['glosses'] = glosses
    # The key is a 2-tuple: (lexeme-form, homograph-number)
    LexiconEntries[(FlexDB.LexiconGetLexemeForm(e),
                    e.HomographNumber)] = data


print "# Entries =", len(LexiconEntries)
# A slice operater can be used to get a subset
for e in sorted(LexiconEntries.items())[:20]:
    print e[0], e[1]    # lexeme-form, homograph-number

