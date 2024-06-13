#
#   check_dict_vs_sort
#
#   June 2011
#
#   Loads the Chinese database and checks all Hanzi vs Pinyin
#   using the Sort string database to check for consistency between
#   the two databases.

import site
site.addsitedir("..\Lib")

from ChineseUtilities import ChineseDB, SortStringDB

# ---------------------------------------------------------------
IgnoreErrors = [
# These are old forms with a 2-syllable pronunciation
'浬',
'瓩',
'吋',
'呎',
'㖊',
'唡',
'哩',
'⿰口畝',
# These have punctuation that isn't handled by SortString
'尼格罗－澳大利亚人种',
'一二·九运动',
]

# ---------------------------------------------------------------
# Checking for Sort File covering all of XD dictionary

HZdict = ChineseDB()
SortDB = SortStringDB()

print("Checking %s against sort file %s" % (HZdict.FileName, SortDB.FileName))

notOk = missingComposed = 0

for e in HZdict:
    sort = SortDB.SortString(e[0], e[1])

    # There are 462 words with composed HZ (using Ideographic Description
    # Characters). 385 of the characters are in char_dat.pkl.
    # The remainder are ignored here for the purpose of this completeness
    # check. (Too obscure to worry about; could be added one day.)
    if "Composed" in sort:
        missingComposed += 1
        continue

    if "[" in sort:
        if e[0] in IgnoreErrors:
            continue

        print(">>", sort, e[0], repr(e[0]), e[1])
        notOk +=1


print("Dictionary entries =", len(HZdict))
print("Sort key entries =", len(SortDB))
print("\tMissing composed characters (ignored) =", missingComposed)
print("\tKnown length mismatches (ignored) =", len(IgnoreErrors))
print()
print("\tUnknown errors =", notOk)

