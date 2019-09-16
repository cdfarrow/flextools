"""convert Tonenum format to Unicode pinyin"""

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

# 2008-3-21 gna
# added licence
# removed unicodedata import
# 2004-1-6 gna
# implemented the e with circumflex code and tests for it
# added unicode_2_0 global for the Arial Unicode MS font
# added {low,mid,high}_vowels variables to simplify regular expressions

from __future__ import unicode_literals
from __future__ import print_function

import re

__all__ = ["tonenum_pinyin"]

unicode_2_0 = False

tones = {}

tones[('a', '1')] = '\N{LATIN SMALL LETTER A WITH MACRON}'
tones[('a', '2')] = '\N{LATIN SMALL LETTER A WITH ACUTE}'
tones[('a', '3')] = '\N{LATIN SMALL LETTER A WITH CARON}'
tones[('a', '4')] = '\N{LATIN SMALL LETTER A WITH GRAVE}'
tones[('a', '5')] = 'a'

tones[('A', '1')] = '\N{LATIN CAPITAL LETTER A WITH MACRON}'
tones[('A', '2')] = '\N{LATIN CAPITAL LETTER A WITH ACUTE}'
tones[('A', '3')] = '\N{LATIN CAPITAL LETTER A WITH CARON}'
tones[('A', '4')] = '\N{LATIN CAPITAL LETTER A WITH GRAVE}'
tones[('A', '5')] = 'A'

tones[('e', '1')] = '\N{LATIN SMALL LETTER E WITH MACRON}'
tones[('e', '2')] = '\N{LATIN SMALL LETTER E WITH ACUTE}'
tones[('e', '3')] = '\N{LATIN SMALL LETTER E WITH CARON}'
tones[('e', '4')] = '\N{LATIN SMALL LETTER E WITH GRAVE}'
tones[('e', '5')] = 'e'

tones[('E', '1')] = '\N{LATIN CAPITAL LETTER E WITH MACRON}'
tones[('E', '2')] = '\N{LATIN CAPITAL LETTER E WITH ACUTE}'
tones[('E', '3')] = '\N{LATIN CAPITAL LETTER E WITH CARON}'
tones[('E', '4')] = '\N{LATIN CAPITAL LETTER E WITH GRAVE}'
tones[('E', '5')] = 'E'

tones[('\N{LATIN SMALL LETTER E WITH CIRCUMFLEX}', '1')] = \
    '\N{LATIN SMALL LETTER E WITH CIRCUMFLEX}\N{COMBINING MACRON}'
tones[('\N{LATIN SMALL LETTER E WITH CIRCUMFLEX}', '2')] = \
    '\N{LATIN SMALL LETTER E WITH CIRCUMFLEX AND ACUTE}'
tones[('\N{LATIN SMALL LETTER E WITH CIRCUMFLEX}', '3')] = \
    '\N{LATIN SMALL LETTER E WITH CIRCUMFLEX}\N{COMBINING CARON}'
tones[('\N{LATIN SMALL LETTER E WITH CIRCUMFLEX}', '4')] = \
    '\N{LATIN SMALL LETTER E WITH CIRCUMFLEX AND GRAVE}'
tones[('\N{LATIN SMALL LETTER E WITH CIRCUMFLEX}', '5')] = \
    '\N{LATIN SMALL LETTER E WITH CIRCUMFLEX}'

tones[('\N{LATIN CAPITAL LETTER E WITH CIRCUMFLEX}', '1')] = \
    '\N{LATIN CAPITAL LETTER E WITH CIRCUMFLEX}\N{COMBINING MACRON}'
tones[('\N{LATIN CAPITAL LETTER E WITH CIRCUMFLEX}', '2')] = \
    '\N{LATIN CAPITAL LETTER E WITH CIRCUMFLEX AND ACUTE}'
tones[('\N{LATIN CAPITAL LETTER E WITH CIRCUMFLEX}', '3')] = \
    '\N{LATIN CAPITAL LETTER E WITH CIRCUMFLEX}\N{COMBINING CARON}'
tones[('\N{LATIN CAPITAL LETTER E WITH CIRCUMFLEX}', '4')] = \
    '\N{LATIN CAPITAL LETTER E WITH CIRCUMFLEX AND GRAVE}'
tones[('\N{LATIN CAPITAL LETTER E WITH CIRCUMFLEX}', '5')] = \
    '\N{LATIN CAPITAL LETTER E WITH CIRCUMFLEX}'

tones[('i', '1')] = '\N{LATIN SMALL LETTER I WITH MACRON}'
tones[('i', '2')] = '\N{LATIN SMALL LETTER I WITH ACUTE}'
tones[('i', '3')] = '\N{LATIN SMALL LETTER I WITH CARON}'
tones[('i', '4')] = '\N{LATIN SMALL LETTER I WITH GRAVE}'
tones[('i', '5')] = 'i'

tones[('I', '1')] = '\N{LATIN CAPITAL LETTER I WITH MACRON}'
tones[('I', '2')] = '\N{LATIN CAPITAL LETTER I WITH ACUTE}'
tones[('I', '3')] = '\N{LATIN CAPITAL LETTER I WITH CARON}'
tones[('I', '4')] = '\N{LATIN CAPITAL LETTER I WITH GRAVE}'
tones[('I', '5')] = 'I'

tones[('o', '1')] = '\N{LATIN SMALL LETTER O WITH MACRON}'
tones[('o', '2')] = '\N{LATIN SMALL LETTER O WITH ACUTE}'
tones[('o', '3')] = '\N{LATIN SMALL LETTER O WITH CARON}'
tones[('o', '4')] = '\N{LATIN SMALL LETTER O WITH GRAVE}'
tones[('o', '5')] = 'o'

tones[('O', '1')] = '\N{LATIN CAPITAL LETTER O WITH MACRON}'
tones[('O', '2')] = '\N{LATIN CAPITAL LETTER O WITH ACUTE}'
tones[('O', '3')] = '\N{LATIN CAPITAL LETTER O WITH CARON}'
tones[('O', '4')] = '\N{LATIN CAPITAL LETTER O WITH GRAVE}'
tones[('O', '5')] = 'O'

tones[('u', '1')] = '\N{LATIN SMALL LETTER U WITH MACRON}'
tones[('u', '2')] = '\N{LATIN SMALL LETTER U WITH ACUTE}'
tones[('u', '3')] = '\N{LATIN SMALL LETTER U WITH CARON}'
tones[('u', '4')] = '\N{LATIN SMALL LETTER U WITH GRAVE}'
tones[('u', '5')] = 'u'

tones[('U', '1')] = '\N{LATIN CAPITAL LETTER U WITH MACRON}'
tones[('U', '2')] = '\N{LATIN CAPITAL LETTER U WITH ACUTE}'
tones[('U', '3')] = '\N{LATIN CAPITAL LETTER U WITH CARON}'
tones[('U', '4')] = '\N{LATIN CAPITAL LETTER U WITH GRAVE}'
tones[('U', '5')] = 'U'

tones[('\N{LATIN SMALL LETTER U WITH DIAERESIS}', '1')] = \
    '\N{LATIN SMALL LETTER U WITH DIAERESIS AND MACRON}'
tones[('\N{LATIN SMALL LETTER U WITH DIAERESIS}', '2')] = \
    '\N{LATIN SMALL LETTER U WITH DIAERESIS AND ACUTE}'
tones[('\N{LATIN SMALL LETTER U WITH DIAERESIS}', '3')] = \
    '\N{LATIN SMALL LETTER U WITH DIAERESIS AND CARON}'
tones[('\N{LATIN SMALL LETTER U WITH DIAERESIS}', '4')] = \
    '\N{LATIN SMALL LETTER U WITH DIAERESIS AND GRAVE}'
tones[('\N{LATIN SMALL LETTER U WITH DIAERESIS}', '5')] = \
    '\N{LATIN SMALL LETTER U WITH DIAERESIS}'

tones[('\N{LATIN CAPITAL LETTER U WITH DIAERESIS}', '1')] = \
    '\N{LATIN CAPITAL LETTER U WITH DIAERESIS AND MACRON}'
tones[('\N{LATIN CAPITAL LETTER U WITH DIAERESIS}', '2')] = \
    '\N{LATIN CAPITAL LETTER U WITH DIAERESIS AND ACUTE}'
tones[('\N{LATIN CAPITAL LETTER U WITH DIAERESIS}', '3')] = \
    '\N{LATIN CAPITAL LETTER U WITH DIAERESIS AND CARON}'
tones[('\N{LATIN CAPITAL LETTER U WITH DIAERESIS}', '4')] = \
    '\N{LATIN CAPITAL LETTER U WITH DIAERESIS AND GRAVE}'
tones[('\N{LATIN CAPITAL LETTER U WITH DIAERESIS}', '5')] = \
    '\N{LATIN CAPITAL LETTER U WITH DIAERESIS}'

tones[('m', '1')] = 'm\N{COMBINING MACRON}'
tones[('m', '2')] = '\N{LATIN SMALL LETTER M WITH ACUTE}'
tones[('m', '3')] = 'm\N{COMBINING CARON}'
tones[('m', '4')] = 'm\N{COMBINING GRAVE ACCENT}'
tones[('m', '5')] = 'm'

tones[('M', '1')] = 'M\N{COMBINING MACRON}'
tones[('M', '2')] = '\N{LATIN CAPITAL LETTER M WITH ACUTE}'
tones[('M', '3')] = 'M\N{COMBINING CARON}'
tones[('M', '4')] = 'M\N{COMBINING GRAVE ACCENT}'
tones[('M', '5')] = 'M'

tones[('n', '1')] = 'n\N{COMBINING MACRON}'
tones[('n', '2')] = '\N{LATIN SMALL LETTER N WITH ACUTE}'
tones[('n', '3')] = '\N{LATIN SMALL LETTER N WITH CARON}'
tones[('n', '4')] = '\N{LATIN SMALL LETTER N WITH GRAVE}'
tones[('n', '5')] = 'n'

tones[('N', '1')] = 'N\N{COMBINING MACRON}'
tones[('N', '2')] = '\N{LATIN CAPITAL LETTER N WITH ACUTE}'
tones[('N', '3')] = '\N{LATIN CAPITAL LETTER N WITH CARON}'
tones[('N', '4')] = '\N{LATIN CAPITAL LETTER N WITH GRAVE}'
tones[('N', '5')] = 'N'

if unicode_2_0:
    # the graphs used above were introduced in Unicode 3.0
    # use these as substitutes for earlier versions
    # Microsoft's Arial Unicode MS font implements Unicode 2.0
    tones[('n', '4')] = 'n\N{COMBINING GRAVE ACCENT}'
    tones[('N', '4')] = 'N\N{COMBINING GRAVE ACCENT}'
    
low_vowels = 'a'
mid_vowels = 'eo' \
    '\N{LATIN SMALL LETTER E WITH CIRCUMFLEX}' \
    '\N{LATIN CAPITAL LETTER E WITH CIRCUMFLEX}'
high_vowels = 'iu'  \
    '\N{LATIN SMALL LETTER U WITH DIAERESIS}' \
    '\N{LATIN CAPITAL LETTER U WITH DIAERESIS}'

ambiguity_pat = re.compile(r'([1-5])([%s%s])' % (low_vowels, mid_vowels), re.I)
old_u_diaeresis_pat = re.compile(r'([ln])(yu)', re.I)
u_diaeresis_pat = re.compile(r'(u)(e?):', re.I)
e_circumflex_pat = re.compile(r'(e)\^', re.I)

tone_pat = re.compile(r'(' + low_vowels +'[' + mid_vowels + high_vowels + \
                      'mngr]*|[' + mid_vowels + '][' + high_vowels + \
                      'mngr]*|[' + high_vowels + \
                      '][mngr]*|m|n[g]*)([1-5])', re.I)

add_apostrophe = r'\1' '\N{RIGHT SINGLE QUOTATION MARK}' r'\2'

char_tones = dict()
for vowel_tone, char in tones.items():
    char_tones[char] = vowel_tone

def old_sub_u_diaeresis(m):
    front, centre = m.groups()
    if centre == 'YU':
        return front + '\N{LATIN CAPITAL LETTER U WITH DIAERESIS}'
    else:
        return front + '\N{LATIN SMALL LETTER U WITH DIAERESIS}'

def sub_u_diaeresis(m):
    centre, tail = m.groups()
    if centre == 'U':
        return '\N{LATIN CAPITAL LETTER U WITH DIAERESIS}' + tail
    else:
        return '\N{LATIN SMALL LETTER U WITH DIAERESIS}' + tail

def sub_e_circumflex(m):
    centre = m.group(1)
    if centre == 'E':
        return '\N{LATIN CAPITAL LETTER E WITH CIRCUMFLEX}'
    else:
        return '\N{LATIN SMALL LETTER E WITH CIRCUMFLEX}'

def sub_tone(m):
    centre, tone = m.groups()
    letter = centre[0]
    tail = centre[1:]
    return tones[(letter, tone)] + tail

def oldtonenum_pinyin(s):
    s = ambiguity_pat.sub(add_apostrophe, s) 
    s = old_u_diaeresis_pat.sub(old_sub_u_diaeresis, s)
    s = tone_pat.sub(sub_tone, s)
    return s

def tonenum_pinyin(s):
    s = ambiguity_pat.sub(add_apostrophe, s)
    s = u_diaeresis_pat.sub(sub_u_diaeresis, s)
    s = e_circumflex_pat.sub(sub_e_circumflex, s)
    s = tone_pat.sub(sub_tone, s)
    return s

if __name__ == "__main__":
    tests = ('a1', 'a2', 'a3', 'a4', 'a5',
            'ao1', 'an2', 'ang3',
            'ia1', 'iao2', 'ian3', 'iang4',
            'ua1', 'uai2', 'uan3', 'uang4',
            'laeio1',
            'A1', 'A2', 'A3', 'A4', 'A5',
            'lAeio1',
            'e1', 'e2', 'e3', 'e4', 'e5',
            'en1', 'eng2',
            'ie3',
            'ueng4',
            '\N{LATIN SMALL LETTER U WITH DIAERESIS}e1',
            'E1', 'E2', 'E3', 'E4', 'E5',
            'i1', 'i2', 'i3', 'i4', 'i5',
            'I1', 'I2', 'I3', 'I4', 'I5',
            'o1', 'o2', 'o3', 'o4', 'o5',
            'ou1', 'ong2',
            'iong3',
            'uo4',
            'O1', 'O2', 'O3', 'O4', 'O5',
            'u1', 'u2', 'u3', 'u4', 'u5',
            'iu1',
            'U1', 'U2', 'U3', 'U4', 'U5',
            'leio1',
            '\N{LATIN SMALL LETTER U WITH DIAERESIS}1', 
            '\N{LATIN SMALL LETTER U WITH DIAERESIS}2',
            '\N{LATIN SMALL LETTER U WITH DIAERESIS}3',
            '\N{LATIN SMALL LETTER U WITH DIAERESIS}4', 
            '\N{LATIN SMALL LETTER U WITH DIAERESIS}5', 
            '\N{LATIN CAPITAL LETTER U WITH DIAERESIS}1', 
            '\N{LATIN CAPITAL LETTER U WITH DIAERESIS}2', 
            '\N{LATIN CAPITAL LETTER U WITH DIAERESIS}3', 
            '\N{LATIN CAPITAL LETTER U WITH DIAERESIS}4', 
            '\N{LATIN CAPITAL LETTER U WITH DIAERESIS}5',
            'er4tong1', 'nar3', 'nar4', 'zher4',
            'Tian1an1men2', 'pi2ao3', 'Xi1an1', 'chang2e2', 'hai3ou1',
            'Tian1 an1 men2', 'pi2 ao3', 'Xi1 an1', 'chang2 e2', 'hai3 ou1',
            'm1', 'm2', 'm3', 'm4', 'm5'
            'n1', 'n2', 'n3', 'n4', 'n5'
            'ng1', 'ng2', 'ng3', 'ng4', 'ng5'
            'M1', 'M2', 'M3', 'M4', 'M5'
            'N1', 'N2', 'N3', 'N4', 'N5'
            'NG1', 'NG2', 'NG3', 'NG4', 'NG5'
            'lyu1', 'nyue2', 'lyue3', 'nyu4',
            'LYU1', 'NYUE2', 'LYue3', 'NyU4',
            'lu:1', 'nue:2', 'lue:3', 'nu:4',
            'LU:1', 'NUE:2', 'Lue:3', 'NU:4',
            'e^1', 'e^2', 'e^3', 'e^4', 'e^5',
            'E^1', 'E^2', 'E^3', 'E^4', 'E^5',
            )
    for i in tests:
        print(('test="%s", ans="%s"' % (i, tonenum_pinyin(i))).encode('utf-8'))
    
