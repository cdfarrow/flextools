#
#   Interactive script for editing the char_data pickle
#

from __future__ import unicode_literals
from __future__ import print_function
from builtins import str

import site
site.addsitedir("..\Lib")

import datafiles


SortData = datafiles.loadSortData()

def sort_pinyin():
    for x in list(SortData.values()):
        if x[1] != sorted(x[1]):
            print("Sorting Pinyin:", x)
            SortData[x[0]] = (x[0], sorted(x[1]), x[2], x[3])

def save():
    sort_pinyin()
    datafiles.saveSortData( SortData )

count = 0
def add_py(key, py):
    global count
    z = SortData[key]
    if py not in z[1]:
        z[1].append(str(py))
        SortData[key] = z
        print(key, z)
        count += 1
    else:
        pass #print("Duplicate Pinyin!")

    
print("Edit Chinese Sort Data")
print("[%s]" % datafiles.SortPickle)
print("%d entries" % len(SortData))
print()
print("Lookup with: SortData['\\u5b50']")
print("\tEntries are tuple: (Chinese, [Pinyin], Stroke count, Strokes)")
print("\tE.g.", SortData['\u5b50'])
print("Add a valid Pinyin pronunciation with: add_py('\\u5b50', 'pin1')")
print("Save data with save()")
