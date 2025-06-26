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

import re

import logging
logger = logging.getLogger(__name__)

ideograph_desc = { 
    '\N{IDEOGRAPHIC DESCRIPTION CHARACTER LEFT TO RIGHT}': 2,
    '\N{IDEOGRAPHIC DESCRIPTION CHARACTER ABOVE TO BELOW}': 2,
    '\N{IDEOGRAPHIC DESCRIPTION CHARACTER LEFT TO MIDDLE AND RIGHT}': 3,
    '\N{IDEOGRAPHIC DESCRIPTION CHARACTER ABOVE TO MIDDLE AND BELOW}': 3,
    '\N{IDEOGRAPHIC DESCRIPTION CHARACTER FULL SURROUND}': 2,
    '\N{IDEOGRAPHIC DESCRIPTION CHARACTER SURROUND FROM ABOVE}': 2,
    '\N{IDEOGRAPHIC DESCRIPTION CHARACTER SURROUND FROM BELOW}': 2,
    '\N{IDEOGRAPHIC DESCRIPTION CHARACTER SURROUND FROM LEFT}': 2,
    '\N{IDEOGRAPHIC DESCRIPTION CHARACTER SURROUND FROM UPPER LEFT}': 2,
    '\N{IDEOGRAPHIC DESCRIPTION CHARACTER SURROUND FROM UPPER RIGHT}': 2,
    '\N{IDEOGRAPHIC DESCRIPTION CHARACTER SURROUND FROM LOWER LEFT}': 2,
    '\N{IDEOGRAPHIC DESCRIPTION CHARACTER OVERLAID}': 2}

class Character(object):
    __slots__ = ('character', 'pronunciations', 'stroke_count', 'strokes')

    def __init__(self, char):
        self.character = char
        self.pronunciations = self.stroke_count = self.strokes = None
    
    def __getstate__(self):
        return (self.character, self.pronunciations, self.stroke_count, self.strokes)

    def __setstate__(self, state):
        self.character, self.pronunciations, self.stroke_count, self.strokes = state

tonenum_syl_pat = re.compile(r"\N{HORIZONTAL ELLIPSIS}|,|;|\?|//|/|\(|\)|[a-z:^]*[1-5]|[1-3]")

def get_tone_syls(tonenum):
    """return a list of the tonenum syllables in tonenum.

    @param tonenum: tonenum
    @type tonenum: string
    @return: syllables in tonenum
    @rtype: list
    """
    syls = list()
    for s in tonenum_syl_pat.findall(tonenum.replace('(r)', '')):
        if s == "//":  # Has to be matched to distinguish from '/'; but not a syllable
            continue
        if len(s) > 3 and s[-2] == 'r' and s[0:-2] != 'er':
            new_s = s[0:-2] + s[-1]
            syls.append(new_s)
            syls.append('er2')
        elif len(s) > 3 and s[-3:-1] == 'r:':   # For 'nur:3"
            new_s = s[0:-3] + s[-2:]
            syls.append(new_s)
            syls.append('er2')
        else:
            syls.append(s)
    return syls

def is_chinese_punctuation(c):
    """Return C{True} if c is Chinese punctuation.

    @param c: a single character
    @type c: string
    @return: True if c is a normal Chinese punctuation
    @rtype: boolean
    """
    
    # codepoints from Unicode 5.0
    ans = False
    if '\u3000' <= c <= '\u303f':
        # CJK Symbols and Punctuation
        ans = True
    elif c == '\N{FULLWIDTH COMMA}':
        ans = True
    elif c == '\N{HORIZONTAL ELLIPSIS}':
        ans = True
    return ans

def is_chinese(c):
    """Return C{True} if c is a Chinese character or punctuation.

    @param c: a single character
    @type c: string
    @return: True if c is a normal Chinese character or punctuation
    @rtype: boolean
    """

    ans = False
    if is_chinese_char(c):
        # Chinese Character
        ans = True
    elif is_chinese_punctuation(c):
        # CJK Symbols and Punctuation
        ans = True
    return ans

def is_chinese_char(c):
    """Return C{True} if c is a Chinese character.

    @param c: a single character
    @type c: string
    @return: True if c is a normal Chinese character
    @rtype: boolean
    """
    
    # codepoints from Unicode 5.0
    ans = False
    if  '\u4e00' <= c <= '\u9fbb':
        # CJK Unified Ideographs
        ans = True
    elif '\u3400' <= c <= '\u4db5':
        # CJK Unified Ideographs Extension A
        ans = True
    elif  '\u020000' <= c <= '\u02a6d6':
        # CJK Unified Ideographs Extension B
        ans = True
    elif '\u2ff0' <= c <= '\u2ffb':
        # Ideographic Description Characters
        ans = True
    return ans

def is_chinese_string(s):
    """
    @param s:
    @type s: string
    @return: True if all characters in s are valid for Chinese
    @rtype: boolean
    """
    ans = True
    for c in s:
        if not is_chinese(c):
            ans = False
    return ans

def get_chars(s):
    """return a list of the characters in s.

    @param s: text in Chinese
    @type s: string
    @return: strings representing single Chinese characters
    @rtype: list of strings
    """
    l = []
    char_desc = ''
    next = 0
    for c in s:
        char_desc += c
        next += ideograph_desc.get(c, 0)
        if next == 0:
            l.append(char_desc)
            char_desc = ''
        else:
            next -= 1
    if next != 0:
        #raise ValueError('unfinished ideographic description sequence, %s' % s)
        logger.warning('unfinished ideographic description sequence, %s' % s)
    return l

nonchar_pat = re.compile( '[  \N{MIDDLE DOT}\N{HORIZONTAL ELLIPSIS}' +
    '\N{FULLWIDTH QUESTION MARK}\N{FULLWIDTH COMMA}' + 
    '\N{FULLWIDTH LEFT PARENTHESIS}\N{FULLWIDTH RIGHT PARENTHESIS}' +
    '\N{LEFT DOUBLE ANGLE BRACKET}\N{RIGHT DOUBLE ANGLE BRACKET}]')

valid_pinyin = set('abcdefghijklmnopqrstuwxyzABCDEFGHIJKLMNOPQRSTUWXYZ12345.: ()/,-…^')
radicals = set('\N{CJK RADICAL FOOT}\N{CJK RADICAL BAMBOO}\N{CJK RADICAL SMALL ONE}\N{CJK RADICAL C-SIMPLIFIED CART}')
chin_paren = set('\N{FULLWIDTH LEFT PARENTHESIS}\N{FULLWIDTH RIGHT PARENTHESIS}')

def check_chinese(std_prons, chinese, tonenum):
    errors = list()
    for c in chinese:
        if not is_chinese(c) and c not in radicals and c not in chin_paren:
            errors.append('non-Chinese character "%s" U+%04x' % (c, ord(c)))
    for c in tonenum:
        if c not in valid_pinyin:
            errors.append('non-pinyin character "%s" U+%04x' % (c, ord(c)))
    # split into syllables and deal with er hua
    tonenums = get_tone_syls(tonenum)
    chars = get_chars(nonchar_pat.sub('', chinese))
    if len(chars) != len(tonenums):
        errors.append('syllable mismatch %s %s' % ('[%s]' % ', '.join(chars), tonenums))
    char_prons = list(zip(chars, tonenums))
    for char, pron in char_prons:
        if char not in std_prons:
            unicode_val = ''
            if len(char) == 1:
                unicode_val = ' U+%04x' % ord(char)
            errors.append('unknown character %s' % char + unicode_val)
        else:
            std_pron = std_prons[char]
            if pron.lower() not in std_pron:
                if pron and pron[-1] == '5':
                    #check if a valid neutral tone
                    pron_seg = pron[:-1]
                    segments = set([p[:-1] for p in list(std_pron)])
                    if pron_seg.lower() not in segments:
                        errors.append('%s [%s]; invalid neutral tone, should be one of %s' % \
                                (char, pron_seg, segments))
                else:
                    errors.append('%s [%s]; pronunciation should be one of %s' % \
                            (char, pron, std_pron))
    return errors

upper_case = set('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
def tonenum_sort_transform(tonenum):
    """return a key for ordering pinyin
    
    @param tonenum: pronunciation of text in C{chin}
    @type tonenum: string
    @return: a key that sorts tonenum in the pinyin order as 
        per Xiandai Hanyu Cidian
    @rtype: tuple of (lowercase tonenum, case) tuples
    """
    key = list()
    for c in tonenum:
        if c in upper_case:
            key.append((ord(c)+32, 1))
        else:
            key.append((ord(c), 1))
    return tuple(key)

def pinyin_sort_transform(char_data, chin, tonenum):
    """return a key for doing a pinyin sort of Chinese in C{chin}.

    @param char_data: Chinese character data used for sorting
    @type char_data:
    @param chin: Chinese text to be sorted
    @type chin: string
    @param tonenum: pronunciation of text in C{chin}
    @type tonenum: string
    @return: a key that sorts the Chinese by pinyin order as 
        per Xiandai Hanyu Cidian
    @rtype: tuple of (tonenum, stroke_count, strokes) triples
    """
    key = []
    chars = [c for c in chin if is_chinese_char(c)]
    for c, c_pron in zip(get_chars(chars), get_tone_syls(tonenum)):
        try:
            char = char_data[c]
        except KeyError:
            logger.warning('unknown character "%s" in "%s"' % (repr(c), chin))
            #might not be the right thing for punctuation
            continue
            #pron = ['']
            #stroke_count = 0
            #strokes = ''
        else:
            #print(char)
            stroke_count = char[2]
            strokes = char[3]
        key.append((tonenum_sort_transform(c_pron), stroke_count, strokes))
    return tuple(key)

def lookup(dict, s):
    """return a list of the characters in s.

    @param s:
    @type s:
    @return:
    @rtype: dictionary
    """
    l = []
    start = 0
    while start < len(s):
        entries = dict.longest_match(s[start:])
        if entries:
            l.append(entries)
            start += len(entries[0].lexeme)
        else:
            logger.warning('missing symbol %s' % s[start])
            l.append(s[start])
            start += 1
    return l

def get_pinyin(entries_seq, entry_sep = ' ', reading_sep = '/'):
    """return a list of the characters in s.

    @param s:
    @type s:
    @return:
    @rtype: dictionary
    """
    l = []
    for entries in entries_seq:
        if isinstance(entries, (str,)):
            if entries == '\n{FULLWIDTH LEFT PARENTHESIS}':
                entries = '('
            elif entries == '\n{FULLWIDTH RIGHT PARENTHESIS}':
                entries = ')'
            elif entries == '\n{FULLWIDTH COMMA}':
                entries = ','
            l.append(entries)
        else:
            # only want unique pronunciations
            prons = set([entry.pronunciation for entry in entries])
            pron_list = [x for x in prons]
            pron_list.sort()
            l.append(reading_sep.join(pron_list))
    return entry_sep.join(l)

def get_english(entries_seq, entry_sep = ' ', sense_sep = '/'):
    """return a list of the characters in s.

    @param s:
    @type s:
    @return:
    @rtype: dictionary
    """
    l = []
    for entries in entries_seq:
        if isinstance(entries, (str,)):
            if entries == '\n{FULLWIDTH LEFT PARENTHESIS}':
                entries = '('
            elif entries == '\n{FULLWIDTH RIGHT PARENTHESIS}':
                entries = ')'
            elif entries == '\n{FULLWIDTH COMMA}':
                entries = ','
            l.append(entries)
        else:
            m = []
            for ent in entries:
                m.append(sense_sep.join(['[%s] %s.' % (s.pos, s.definition) for s in ent.senses]))
            l.append('|'.join(m))
    return entry_sep.join(l)

def normalise_tonenum(s):
    """remove unwanted things from the tonenum. For the moment this just means
    make it lower case and remove the optional er hua.
    return a list of the characters in s.

    @param s:
    @type s:
    @return:
    @rtype: dictionary
    """
    #return s.lower().replace('(r)')
    return s.replace('(r)', '').replace('//', '')

def to_xhc_tonenum(s):
    """return a list of the characters in s.

    @param s:
    @type s:
    @return:
    @rtype: dictionary
    """
    return s.replace('r:', ':r').replace('ue:', 'u:e').replace('\u00b7', '.')

def from_xhc_tonenum(s):
    """return a list of the characters in s.

    @param s:
    @type s:
    @return:
    @rtype: dictionary
    """
    return s.replace('.', '\u00b7')

def to_semdom_tonenum(s):
    """return a list of the characters in s.

    @param s:
    @type s:
    @return:
    @rtype: dictionary
    """
    return s.replace('(r)', '').replace('ue:', 'u:e').replace('//', '').replace('\u00b7', '.')

def from_semdom_tonenum(s):
    """return a list of the characters in s.

    @param s:
    @type s:
    @return:
    @rtype: dictionary
    """
    return s.replace('u:e', 'ue:').replace(':r', 'r:').replace('.', '\u00b7')
