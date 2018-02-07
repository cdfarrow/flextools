# -*- coding: cp1252 -*-

# Report_Collocations.py
#
# An EXAMPLE module that uses the NLTK (Natural Language Toolkit)
# to calculate collocations from the Texts in a FLEx database.
# See: http://www.nltk.org
#
# NOTE: tokenising the texts will require using functions that
#       are appropriate to your language. For example, the Python
#       string function split() will divide at white-space keeping
#       punctuation attached to wordforms. nltk.word_tokenize()
#       is English-oriented and will parse "can't" as a token, but
#       it doesn't handle extended characters (eg IPA, letters with
#       diacritics, etc.)
#
# C D Farrow
# August 2009
#
# Platforms: Python .NET and IronPython
#

# Configure the path to find the library modules.
import site
site.addsitedir("../")

from FLExDBAccess import FLExDBAccess

import nltk


#----------------------------------------------------------------
# Configurables:

FLExDBName           = "Sena 3"

#----------------------------------------------------------------


# If your data doesn't match your system encoding (in the console) then
# redirect the output to a file: this will make it utf-8.
## BUT This doesn't work in IronPython!!
import codecs
import sys
if sys.stdout.encoding == None:
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout)


FlexDB = FLExDBAccess()

# No name opens the first db on the default server
if not FlexDB.OpenDatabase(FLExDBName, verbose = True):
    sys.exit(1)

# Do some analysis of the Texts

## All texts in one collocation analysis:
allTexts = "\n\n".join(list(FlexDB.TextsGetAll(supplyName=False)))
nText = nltk.Text(allTexts.split(), "Null")
print nText.collocations()
print

## Each text individually analysed:
for name, text in FlexDB.TextsGetAll_Iterator():
    print ">>>>", name, "<<<<"
    print text
    print

    ## Need to tokenise according to language
    ##    ## nltk.word_tokenize handles English, but not IPA letters.
    nText = nltk.Text(text.split(), name)
    print nText.collocations()
    print

    
