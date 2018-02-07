# -*- coding: cp1252 -*-

# Check_ExampleFields.py
#
# An EXAMPLE module for checking for good data in a particular field.
# E.g. Making sure that example sentences end with correct punctuation.
#
# C D Farrow
# July 2008
#
# Platforms: Python .NET and IronPython
#

# Configure the path to find the library modules.
import site
site.addsitedir("../")

from FLExDBAccess import FLExDBAccess

import re
import operator

#----------------------------------------------------------------
# Configurables:

FLExDBName           = "Sena 3"

TestNumberOfEntries  = -1   # -1 for whole DB; else no. of db entries to scan
AppendReportToEndOfField = False
ReportFieldName = "FT_Flags"

TestSuite = [
    (re.compile(r"[?!\.]{1}$").search, False, "ERR:no-ending-punc"),
    (re.compile(r"[?!\.]{2,}$").search, True, "ERR:too-much-punc")

    ]

#----------------------------------------------------------------


# If your data doesn't match your system encoding (in the console) then
# redirect the output to a file: this will make it utf-8.
# Requires IronPython 2.6+
import codecs
import sys
print "Stdout encoding =", sys.stdout.encoding
##if sys.stdout.encoding == None:
sys.stdout = codecs.getwriter("utf-8")(sys.stdout)
       



#============ Open the database ===============

FlexDB = FLExDBAccess()

# No name opens the first db on the default server
if not FlexDB.OpenDatabase(FLExDBName, verbose = True):
    print "FDO Cache Create failed!"
    sys.exit(1)
       

#===================

limit = TestNumberOfEntries

if limit > 0: print "TEST: Scanning first", limit, "entries..."
else: print "Scanning", FlexDB.LexiconNumberOfEntries(), "entries..."



reportField = FlexDB.LexiconGetSenseCustomFieldNamed(ReportFieldName)
if not reportField:
    print "WARNING: FT_Flags field not found"
    AppendReportToEndOfField = False

for e in FlexDB.LexiconAllEntries() :
    context = ["",""]
    context[0] = r"\lx " + FlexDB.LexiconGetLexemeForm(e) 
    print context[0]
    for sense in e.SensesOS :
        for example in sense.ExamplesOS:
            exText = FlexDB.LexiconGetExample(example, 14964)
            if exText  == None:
                print "\n".join(context)
                print "Blank example!"
                continue
            context[1] = r"\ex " + exText
            
            for testFunction, result, message in TestSuite:
                if operator.truth(testFunction(exText)) == result:
                    print "\n".join(context)
                    print "==>", message
                    if AppendReportToEndOfField:
                        FlexDB.LexiconAddTagToField(sense.Hvo,
                                                    reportField,
                                                    message)
                    ### CHANGES the DB
                    ### FlexDB.LexiconSetExample(example, exText + "X", 14964)
        
    print
    if limit > 0:
        limit -= 1
    elif limit == 0:
        break
