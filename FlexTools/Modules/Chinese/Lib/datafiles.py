#
#   datafiles
#
#   References to the Chinese data files, including load/save functions
#   for char_dat.pkl.
#

import os
import pickle

datapath = os.path.join(os.path.dirname(__file__), "Datafiles")


SortDB = os.path.join(datapath, "ch2sort.txt")
DictDB = os.path.join(datapath, "xhc4_words.txt")
SortPickle = os.path.join(datapath, "char_dat.pkl")


def loadSortData(fname=SortPickle):
    with open(fname, 'rb') as file:
        SortData = pickle.load(file)
    return SortData

def saveSortData(SortData, fname=SortPickle):
    with open(fname, 'wb') as file:
        pickle.dump(SortData, file)
    
