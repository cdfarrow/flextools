#!/usr/bin/env python
# -*- coding: utf8 -*-

# pinyin_checker 1.0, released 21 March 2008

# Copyright 2008 Greg Aumann

# This file is part of pinyin_checker

# pinyin_checker is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

"""Module docstring.

This serves as a long usage message.
"""

import segmenter
import chin_utils
import logging
import re

def get_tonenum_dict(fname):
    """return a dictionary of tonenums keyed by lexeme
    
    @param fname: name of the dictionary file
    @type fname: string
    @return: list of Chinese lexemes with pronunciations
    @rtype: list of tuples
    """
    word_file = open(fname)
    line_num = 0
    word_tonenum = list()
    digits = set(u'123456789')
    removeR = re.compile(r"(?<=[a-z]{2})r(?=[:1-5])")
    #char_prons = get_xhc_char_prons()
    for line in word_file:
        line_num += 1
        line = line.decode('utf8').strip()
        fields = line.split('\t')
        if len(fields) != 2:
            logging.error("line %d: num of fields != 2" %  line_num)
        else:
            chinese, tonenum = fields
            # perhaps should skip at this point
            if chinese[-1] == u'*':
                chinese = chinese[:-1]
            if chinese[-1] in digits:
                chinese = chinese[:-1]
            # maybe don't want to do this
            tonenum = tonenum.replace('(r)', '')
            # get rid of erhua
            if u'（儿）' in chinese:
                # include with erhua
                word_tonenum += ((chinese.replace(u'（儿）', u'儿'), tonenum),)
                # and without erhua
                tonenum 
                word_tonenum += ((chinese.replace(u'（儿）', ''),
                                  removeR.sub("", tonenum)),)
            else:
                word_tonenum += ((chinese, tonenum),)
    return word_tonenum

punctuation = {
    u'\N{IDEOGRAPHIC COMMA}': u', ',
    u'\N{FULLWIDTH COMMA}': u', ',
    u'\N{IDEOGRAPHIC FULL STOP}': u'. ',
    u'\N{FULLWIDTH SEMICOLON}': u'; ',
    u'\N{FULLWIDTH COLON}': u': ',
    u'\N{HORIZONTAL ELLIPSIS}': u'…',
    u'\N{FULLWIDTH QUESTION MARK}': u'? ',
    u'\N{FULLWIDTH EXCLAMATION MARK}': u'! ',
    u'\N{FULLWIDTH LEFT PARENTHESIS}': u' (',
    u'\N{FULLWIDTH RIGHT PARENTHESIS}': u') ',
    u'\N{FULLWIDTH LEFT SQUARE BRACKET}': u' [',
    u'\N{FULLWIDTH RIGHT SQUARE BRACKET}': u'] ',
    u'\N{LEFT DOUBLE ANGLE BRACKET}': u' <<',
    u'\N{RIGHT DOUBLE ANGLE BRACKET}': u'>> ',
    u'“': u' \N{LEFT DOUBLE QUOTATION MARK}',
    u'”': u'\N{RIGHT DOUBLE QUOTATION MARK} ',
    u'‘': u' \N{LEFT SINGLE QUOTATION MARK}',
    u'’': u'\N{RIGHT SINGLE QUOTATION MARK} ',
    u'/': u'/',         # Allow '/' for gloss separation
    u'1': u'1 ',        # Allow '1' - '3' for person-marking in glosses
    u'2': u'2 ',
    u'3': u'3 ',
    u'\n': u'\n',
}

def startdict_to_string(start_dict):
    l = list()
    for key in sorted(start_dict):
        l.append("'%s': %s" % (key, str(start_dict[key])))
    return '\n'.join(l)

def segments(s, positions):
    """return a list of segments"""
    segs = list()
    for i, pos in enumerate(positions[:-1]):
        segs.append(s[pos:positions[i+1]])
    return segs

def join_segments(sgmtr, s, positions):
    segs = segments(s, positions)
    tonenum = list()
    for i, seg in enumerate(segs[:-1]):
        tonenum.append('|'.join(sorted(list(sgmtr.values(seg)))))
        if (seg not in punctuation) and (segs[i+1] not in punctuation):
            tonenum.append(' ')
    if len(segs) > 0:
        seg = segs[-1]
        tonenum.append('|'.join(sorted(list(sgmtr.values(seg)))))
    else:
        logging.warning('no segments found')
    return ''.join(tonenum)

def check_pinyin(sgmtr, hanzi, pinyin):
    def __check_hanzi_with_pinyin(matches):
        hz_segs = segments(hanzi, matches)
        eq = True
        # Divides by spaces into pinyin segments
        # Jul2016: This doesn't handle punctuation.
        # Could use modified version of chin_utils.get_tone_syls()
        # (It handles punctuation, but splits pinyin into separate syllables)
        py_segs = pinyin.split()  
        if len(py_segs) == len(hz_segs):
            for py, hz in zip(py_segs, hz_segs):
                if py not in sgmtr.values(hz):
                    eq = False
                    break
        else:
            eq = False
        return eq

    errors = list()
    if hanzi:
        l = sgmtr.match_all_ends(hanzi)
        r = sgmtr.match_all_starts(hanzi)
        if l == r:
            try:
                tonenum = join_segments(sgmtr, hanzi, l).strip()
            except KeyError, msg:
                errors.append('\thanzi %s: Unknown Chinese: %s' % (hanzi, msg))
            else:
                if pinyin:
                    if pinyin != tonenum:
                        if not __check_hanzi_with_pinyin(l):
                            errors.append('hanzi %s: Expected "%s"' % (hanzi, tonenum))
##                        else:
##                            logging.info('\thanzi %s: gp "%s" segments as expected' % (hanzi, tonenum))
##                    else:
##                        logging.info('\thanzi %s: gp "%s" as expected' % (hanzi, tonenum))
##                else:
##                    logging.info('\thanzi %s: adding pinyin "%s"' % (hanzi, tonenum))
        else:
            if pinyin:
                if not (__check_hanzi_with_pinyin(l) or\
                        __check_hanzi_with_pinyin(r)):
                    errors.append('hanzi %s: Expected "%s" or "%s"'
                                  % (hanzi,
                                     join_segments(sgmtr, hanzi, l).strip(),
                                     join_segments(sgmtr, hanzi, r).strip()))
            else:
                errors.append('hanzi %s: ambiguous segmentation LTR="%s", RTL="%s"' % 
                    (hanzi, '|'.join(segments(hanzi, l)),
                    ('|'.join(segments(hanzi, r)))))
    return errors

def init_chin_sgmtr(dict_files):
    chin_sgmtr = segmenter.MaximalMatch()
    for fname in dict_files:
        word_tonenum = get_tonenum_dict(fname)
        chin_sgmtr.add_segment_values(word_tonenum)
    chin_sgmtr.add_segment_values(punctuation.items())
    return chin_sgmtr
