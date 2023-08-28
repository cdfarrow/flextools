# -*- coding: utf-8 -*-
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
import datafiles, os

# ---------------------------------------------------------------

# ---------------------------------------------------------------
# Checking for Sort File covering all of XD dictionary

OldSortDB = SortStringDB(os.path.join(datafiles.datapath, r"Archive\ch2sort_2004(utf8).txt"))
SortDB = SortStringDB()

print("Checking %s against sort file %s" % (OldSortDB.FileName, SortDB.FileName))

notOk = missingComposed = 0

for e in sorted(OldSortDB.items()):
##    print(e)
    try:
        sort = SortDB[e[0]]
    except KeyError:
        print("Not in latest DB:", repr(e[0]))
        continue
        
    if sort != e[1]:
        if len(sort) < len(e[1]):
            notOk += 1
            print(e[0], list(sort.keys()), "!=", list(e[1].keys()))


for i in ['\u602b', '\u602b\u7136']: print(i)

##print("Dictionary entries =", len(HZdict))
##print("Sort key entries =", len(SortDB))
##print("\tMissing composed characters (ignored) =", missingComposed)
##print("\tKnown length mismatches (ignored) =", len(IgnoreErrors))
##print()
print("\tUnknown errors =", notOk)
##
##
