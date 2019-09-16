#
#   extract_pkl2sort
#
#   Reads char_dat.pkl and writes out a fresh ch2sort.txt from it.
#   

from __future__ import unicode_literals
from __future__ import print_function

import site
site.addsitedir("..\Lib")

from ChineseUtilities import MakeSortString

import datafiles
sortData = datafiles.loadSortData()

import codecs
f = codecs.open(datafiles.SortDB,'w','utf-8','strict')



count = 0
for c, d in sortData.items():
    # c is Hanzi
    # d is list of [chr, pinyin, # strokes, order of strokes by type]

    # Skip the composite characters (not-in-Unicode glyphs)
    #if len(c) > 1 :
    #    continue
    
    f.write('%s' % c)
    for py in d[1]:
        f.write('\t%s\t%s' % (py, MakeSortString(py, d[2], d[3])))
        
    f.write('\r\n')
    count += 1

f.close()

print("%s written with %d entries." % (datafiles.SortDB, count))

