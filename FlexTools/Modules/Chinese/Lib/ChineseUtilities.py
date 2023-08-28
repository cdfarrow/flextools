# -*- coding: utf-8 -*-
#
#   ChineseUtilities
#
#   Craig Farrow
#   May 2011
#
#   Support functions for processing Chinese and Pinyin in FLExTools.
#
#

import codecs
import re

import os, sys

import datafiles
from chin_utils import *
from check_pinyin import *
from pinyin import *


# --- Chinese Writing Systems ---


def ChineseWritingSystems(project, report, Hanzi=False, Tonenum=False, Pinyin=False, Sort=False):
    """
    Returns a list of Language Tags for the requested Chinese writing systems.
    Checks for 'zh-CN' ones first, then 'cmn' ones as an alternative (for
    projects created in FW v6 or earlier).
    """

    def __getWS(languageTag, alternateTag):
        name = project.WSUIName(languageTag)         # Check WS exists
        if not name:
            name = project.WSUIName(alternateTag)    # Try alternate
            if not name:
                report.Warning("Writing system not found: %s" % languageTag)
                return None
            return alternateTag
        return languageTag                      # Pass the Tag around

    WSs = []
    if Hanzi:
        WSs.append(__getWS('zh-CN', 'cmn'))

    if Tonenum:
        WSs.append(__getWS('zh-CN-X-PYN', 'cmn--X-PYN'))

    if Pinyin:
        WSs.append(__getWS('zh-CN-X-PY', 'cmn--X-PY'))

    if Sort:
        WSs.append(__getWS('zh-CN-X-ZHSORT', 'cmn--ZHSORT'))

    return WSs


# --- Chinese Database helper functions and classes ---

class ChineseDB(list):
    def __init__(self, fname=datafiles.DictDB):
        list.__init__(self)
        self.FileName = fname
        self.extend(get_tonenum_dict(fname))


class ChineseParser(object):
    def __init__(self, fname=datafiles.DictDB):
        self.segmenter = init_chin_sgmtr([fname])

    def Tonenum(self, hanzi, tonenum):
        # Copied and adapted from check_pinyin.check_pinyin()
        def __check_hanzi_with_pinyin(matches):
            hz_segs = segments(hanzi, matches)
            eq = True
            # Divides by spaces into pinyin segments
            # Jul2016: This doesn't handle punctuation.
            # Could use modified version of chin_utils.get_tone_syls()
            # (It handles punctuation, but splits pinyin into separate syllables)
            py_segs = tonenum.split()
            if len(py_segs) == len(hz_segs):
                for py, hz in zip(py_segs, hz_segs):
                    if py not in self.segmenter.values(hz):
                        eq = False
                        break
            else:
                eq = False
            return eq

        if hanzi:
            hanzi = hanzi.strip()
            l = self.segmenter.match_all_ends(hanzi)
            r = self.segmenter.match_all_starts(hanzi)
            if l == r:
                try:
                    newTonenum = join_segments(self.segmenter, hanzi, l).strip()
                except KeyError as msg:
                    ch = str(msg)
                    if ch =="u'.'" and "..." in hanzi:
                        return "[Use Ellipsis (U+2026): %s]" % msg
                    elif ch in ["u'('", "u')'", "u'['", "u']'", "u';'", "u'.'", "u' '", "u'-'"]:
                        return "[Use Chinese (wide) punctuation: %s]" % msg
                    return "[Unknown/unsupported Chinese : %s]" % msg

                if not tonenum:
                    return newTonenum

                if newTonenum != tonenum:
                    if __check_hanzi_with_pinyin(l):
                        return None
                    else:
                        return '[Expected "%s"]' % newTonenum
            else:
                # Ambiguous parse
                try:
                    tonenum1 = join_segments(self.segmenter, hanzi, l).strip()
                    tonenum2 = join_segments(self.segmenter, hanzi, r).strip()
                except KeyError as msg:
                    ch = str(msg)
                    if ch =="u'.'" and "..." in hanzi:
                        return "[Use Ellipsis (U+2026): %s]" % msg
                    elif ch in ["u'('", "u')'", "u'['", "u']'", "u';'", "u'.'", "u' '", "u'-'"]:
                        return "[Use Chinese (wide) punctuation: %s]" % msg
                    return "[Unknown/unsupported Chinese : %s]" % msg

                newTonenum = " | ".join((tonenum1, tonenum2))
                if not tonenum:
                    return newTonenum

                if newTonenum != tonenum:
                    if (__check_hanzi_with_pinyin(l) or\
                        __check_hanzi_with_pinyin(r)):
                        return None           # All okay; no change
                    else:
                        return '[Expected "%s"]' % newTonenum.replace(' | ', '" or "')
        return None

    def CalculateTonenum(self, hanzi, tonenum):
        # Calculates the Tonenumber for the given Hanzi, AND compares that with
        # the tonenum parameter.
        # Returns a tuple: (newTonenum, msg)
        #   newTonenum: Calculated Tonenumber. (Note this will be an empty string if hz is empty)
        #               None if the field is not to be written
        #               (i.e. it is already correct, or there was an error)
        #   msg: None, or a warning message about the data.

        newTonenum = msg = None
        if hanzi:
            newTonenum = self.Tonenum(hanzi, tonenum)
            if newTonenum and "[" in newTonenum:   # Warning message, don't write field
                if tonenum:
                    msg = "(%s; %s): %s" % (hanzi, tonenum, newTonenum)
                else:
                    msg = "%s: %s" % (hanzi, newTonenum)
                newTonenum = None
        else:
            if tonenum:              # Set to blank if the Chinese has been deleted
                newTonenum = ""

        return (newTonenum, msg)

# --- Tone number to Pinyin

def TonenumberToPinyin(tonenum):
    return tonenum_pinyin(tonenum)

# --- Sort String functions and classes ---

def MakeSortString(py, stroke_count, strokes):
    # The Stroke count is represented as letters to make it distinguishable
    # from the tone number. '@' is used for zero.
    ssmap = ['@','A','B','C','D','E','F','G','H','I']
    stroke_count = ssmap[stroke_count // 10] + ssmap[stroke_count % 10]
    # The default ICU sort in Fieldworks ignores punctuation, so
    # we change ':' to '9' so '5' < u-diaresis < 'a'
    # E.g. lu4 < lu94 < luan
    py = py.replace(':', '9')
    return "".join([py, stroke_count, strokes])


class SortStringDB(dict):

    def __init__(self, fname=datafiles.SortPickle):
        dict.__init__(self)
        self.FileName = fname
        self.__load()

    def __loadFromTextFile(self, fname):
        try:
            f = codecs.open(fname, encoding="utf-8")
        except IOError:
            print("File not found!")
            return

        for line in f.readlines():
            line = line.strip("\n\r")
            parts = line.split("\t")

            mapping = {}
            hz = parts.pop(0)
            if len(parts) % 2 == 0:
                while (parts):
                    py = parts.pop(0)
                    sortKey = parts.pop(0)
                    mapping[py] = sortKey
                self[hz] = mapping

        f.close()

    def __loadFromPickle(self, fname):
        sortData = datafiles.loadSortData(fname)

        for d in list(sortData.values()):
            # d is list of [chr, pinyin, # strokes, order of strokes by type]
            mapping = {}
            for py in d[1]:
                mapping[py] = MakeSortString(py, d[2], d[3])
            self[d[0]] = mapping

    def __loadPunctuation(self):
        # Extra punctuation and numerals used in Chinese text

        for c, l in list(punctuation.items()): # from check_pinyin.py
            l = l.strip()
            self[c] = {l: l}            # Sort string is itself for punctuation

    def __load(self):
        # This stack-frame code is all that I've found to work for
        # getting the current path from Idle, command-line AND
        # FlexTools (where it is used by a custom-imported module.)
        # (Use of __file__ failed for Idle)
        mypath = os.path.dirname(sys._getframe().f_code.co_filename)
        fname = os.path.join(mypath, self.FileName)

        if fname[-4:] == ".pkl":
            self.__loadFromPickle(fname)
        else:
            self.__loadFromTextFile(fname)
        self.__loadPunctuation()

    def Lookup(self, hz, py):
        try:
            sortInfo = self[hz]
        except KeyError:
            if len(hz) > 1:
                return "[Composed HZ not in DB: %s]" % repr(hz)
            else:
                return "[HZ not in DB: %s]" % repr(hz)
        try:
            return sortInfo[py]
        except KeyError:
            return "[PY mismatch]"


    def SortString(self, hz, py):
        """
        Return a string that will produce an alphabetical sort for the supplied
        Chinese (hz) and Pinyin with tone numbers (py).
        If there are any errors then the relevant segment will have an
        error message contained in square brackets [].
        """
        if not hz or not py:
            return ""

        hzList = get_chars(hz)
        pyList = get_tone_syls(py.lower())

        if len(hzList) != len(pyList):
            return "[PY different length]"

        return ";".join([self.Lookup(h,p) for h, p in zip(hzList, pyList)])

    def CalculateSortString(self, hanzi, tonenum, sortString):
        # Calculates the Sort String for the given Hanzi and Tonenumber,
        # AND compares that with the sortString parameter.
        # Returns a tuple: (newSortString, msg)
        #   newSortString: Calculated Sort String.
        #                  (Note this will be an empty string if hz or tonenum is empty,
        #                   or there is an error.)
        #                  None if the field is not to be written (i.e. it is already correct)
        #   msg: None, or a warning message about the data.

        newSortString = msg = None
        if hanzi and tonenum:
            if "|" in tonenum:
                msg = "Ambiguous tone number: %s" % tonenum
                # Clear the sort string field if ambiguity in
                # the tonenum field hasn't been resolved
                newSortString = ""
            else:
                newSortString = self.SortString(hanzi, tonenum)
                if '[' in newSortString:
                    msg = "(%s, %s) - %s" % (hanzi, tonenum, newSortString)
                    newSortString = ""
        else:
            newSortString = ""     # Clear if hanzi or tonenum are blank

        if newSortString == sortString:     # Don't write if no change
            newSortString = None

        return (newSortString, msg)

