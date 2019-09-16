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

"""
functions for doing word segmentation.
"""
import logging

class MaximalMatch(object):
    """
    """
    def __init__(self):
       self._beginnings = dict()
       self._endings = dict()
       self.max_length = 0
       
    def add_segment_values(self, segment_values):
        """add a sequence of known segments and their values. 
        
        Can be called multiple times. Return a dictionary of starting and ending phrases of the lexemes.
        If a character sequence occurs as the start/end of a lexical entry but not as
        a lexical entry then it is in the dictionary with value None. If a character
        sequence occurs as a lexical entry (regardless of whether it also occurs
        at the start of another lexical entry) then its value is a set of possible
        values. 
        
        @param segments: list of (or iterator over) valid segments
        @type segments: iterable
        """
        beginnings = self._beginnings
        endings = self._endings
        for segment, value in segment_values:
            # put the lexeme in the dictionaries
            cur_value = beginnings.setdefault(segment, set())
            if cur_value is None:
                beginnings[segment] = cur_value = set()
            cur_value.add(value)
            endings[segment] = cur_value
            #put beginning strings in the dictionary
            seg_start = ''
            for seg in segment[:-1]:
                seg_start += seg
                beginnings.setdefault(seg_start, None)
            #put ending strings in the dictionary
            seg_end = ''
            for seg in reversed(segment[1:]):
                seg_end = seg + seg_end
                endings.setdefault(seg_end, None)    

    def values(self, segment):
        """return the value of the segment
        
        @param segment: 
        @type: hashable sequence
        @return: all values of the segment
        @rtype: set of values
        """
        return self._beginnings[segment]
        
    def match_end(self, s, start=0):
        """"return the endpoint of the longest segment from position start.
        
        @param s: text to be segmented
        @type s: indexable sequence
        @param start: position to look for match from
        @type start: integer
        @return: the endpoint of the match such that it is contained in the 
            contained in the range [start, end]. If no match is found then 
            -1 is returned
        @rtype: integer
        """
        beginnings = self._beginnings
        last_match = p = ''
        for c in s[start:]:
            p += c
            try:
                value = beginnings[p]
                if value is not None:
                    # keep track of last real entry
                    last_match = p
            except KeyError:
                break
        if last_match == '':
            return -1
        else:
            return start + len(last_match)

    def match_start(self, s, end=None):
        """"return the start point of the longest segment to position end.
        
        @param s: text to be segmented
        @type s: indexable sequence
        @param end: position to look for match to
        @type end: integer
        @return: the endpoint of the match such that it is contained in the 
            contained in the range [retval, end]. If no match is found then 
            -1 is returned
        @rtype: integer
        """
        if end is None:
            end = len(s)
        endings = self._endings
        last_match = p = ''
        for c in reversed(s[:end]):
            p = c + p
            try:
                value = endings[p]
                if value is not None:
                    # keep track of last real entry
                    last_match = p
            except KeyError:
                break
        if last_match == '':
            return -1
        else:
            return end - len(last_match)

    def match_all_ends(self, s):
        """Return a list of all positions in s that have a match
        for example if C{s='abcde'} and valid segments are 'ab' and 'de' then
        it returns C{[0, 2, 3]}. 
        @param s: sequence of 
        @type s: sequence
        @return: list of all positions 
        @rtype: list
        """
        pos = 0
        l = list()
        while pos < len(s) :
            l.append(pos)
            end = self.match_end(s, pos)
            if end == -1:
                pos += 1
            else:
                pos = end
        l.append(pos)
        return l

    def match_all_starts(self, s):
        pos = len(s)
        l = list()
        while pos > 0:
            l.append(pos)
            start = self.match_start(s, pos)
            if start == -1:
                pos -= 1
            else:
                pos = start
        l.append(pos)
        l.reverse()
        return l

class MaximalMatch_old(object):
    """
    """
    def __init__(self):
       self._beginnings = set()
       self._endings = set()
       self.max_length = 0
       
    def add_segments(self, segments):
        """add a sequence of known segments. 
        
        Can be called multiple times. Return a dictionary of starting and ending phrases of the lexemes.
        If a character sequence occurs as the start/end of a lexical entry but not as
        a lexical entry then it is in the dictionary with value None. If a character
        sequence occurs as a lexical entry (regardless of whether it also occurs
        at the start of another lexical entry) then its value is a set of possible
        values. 
        
        @param segments: list of (or iterator over) valid segments
        @type segments: iterable
        """
        beginnings = self._beginnings
        endings = self._endings
        for seg in segments:
            length = len(seg)
            if length > self.max_length:
                self.max_length  = length
            #put beginning strings in the set
            beg = ''
            for c in seg:
                beg += c
                beginnings.add(beg)
            #put ending strings in the set
            end = ''
            for c in reversed(seg):
                end = c + end
                endings.add(end)

    def match_from(self, s, start=0):
        """"return the endpoint of the longest segment from position start.
        
        @param s: text to be segmented
        @type s: indexable sequence
        @param start: position to look for match from
        @type start: integer
        @return: the endpoint of the match such that it is contained in the 
            contained in the range [start, end]. If no match is found then 
            -1 is returned
        @rtype: integer
        """
        end = start + 1
        beginnings = self._beginnings
        length = len(s)
        while end <= length:
            if s[start:end] in beginnings:
                end += 1
            else:
                end -= 1
                break
        if end > length:
            end = length
        elif end == start:
            end = -1
        return end

    def match_to(self, s, end=None):
        """"return the startpoint of the longest segment to position end.
        
        @param s: text to be segmented
        @type s: indexable sequence
        @param end: position to look for match to
        @type end: integer
        @return: the endpoint of the match such that it is contained in the 
            contained in the range [retval, end]. If no match is found then 
            -1 is returned
        @rtype: integer
        """
        if end is None:
            end = len(s)
        start = end - 1
        endings = self._endings
        while start >= 0:
            if s[start:end] in endings:
                start -= 1
            else:
                start += 1
                break
        if start < 0:
            start = 0
        elif start == end:
            start = -1
        return start

    def match_from_all(self, s):
        """Return a list of all positions in s that have a match
        for example if C{s='abcde'} and valid segments are 'ab' and 'de' then
        it returns C{[0, 2, 3]}. 
        @param s: sequence of 
        @type s: sequence
        @return: list of all positions 
        @rtype: list
        """
        pos = 0
        l = list()
        while pos < len(s) :
            l.append(pos)
            end = self.match_from(s, pos)
            if end == -1:
                pos += 1
            else:
                pos = end
        l.append(pos)
        return l

    def match_to_all(self, s):
        pos = len(s)
        l = list()
        while pos > 0:
            l.append(pos)
            start = self.match_to(s, pos)
            if start == -1:
                pos -= 1
            else:
                pos = start
        l.append(pos)
        l.reverse()
        return l

def make_start_dict(lexeme_values):
    """Return a dictionary of starting phrases of the lexemes.
    If a character sequence occurs as the start of a lexical entry but not as
    a lexical entry then it is in the dictionary with value None. If a character
    sequence occurs as a lexical entry (regardless of whether it also occurs
    at the start of another lexical entry) then its value is a list of possible
    ids. 
    
    @param lexeme_values: iterator over (lexeme, value) tuples
    @type lexeme_values: iterator
    @return: dictionary of valid segments and initial portions of valid 
        segments. If the segment is valid it has a value. Initial portions 
        of valid segments are in the dictionary with the value None.
        Thus if 'abcd' is the valid segment with value 42 then the dictionary is
        {'abcd': 42, 'abc': None, 'ab': None, 'a': None}
        if 'ab' is also a valid segment with value 23 then the dictionary is
        {'abcd': 42, 'abc': None, 'ab': 23, 'a': None}
    @rtype: dictionary
    """
    start_dict = dict()
    for lexeme, value in lexeme_values:
        # put the lexeme in the dictionary
        cur_value = start_dict.setdefault(lexeme, set())
        if cur_value is None:
            start_dict[lexeme] = cur_value = set()
        cur_value.add(value)
        #put beginning strings in the dictionary
        lex_start = ''
        for segment in lexeme:
            lex_start += segment
            start_dict.setdefault(lex_start, None)
    return start_dict

def add_to_start_end_dicts(start_dict, end_dict, lexeme_values):
    """Return a dictionary of starting and ending phrases of the lexemes.
    If a character sequence occurs as the start/end of a lexical entry but not as
    a lexical entry then it is in the dictionary with value None. If a character
    sequence occurs as a lexical entry (regardless of whether it also occurs
    at the start of another lexical entry) then its value is a set of possible
    values. 
    
    @param lexeme_values: iterator over (lexeme, value) tuples
    @type lexeme_values: iterator
    @return: dictionary of valid segments and initial portions of valid 
        segments. If the segment is valid it has a value. Initial portions 
        of valid segments are in the dictionary with the value None.
        Thus if 'abcd' is the valid segment with value 42 then the dictionary is
        {'abcd': 42, 'abc': None, 'ab': None, 'a': None}
        if 'ab' is also a valid segment with value 23 then the dictionary is
        {'abcd': 42, 'abc': None, 'ab': 23, 'a': None}
    @rtype: dictionary
    """
    for lexeme, value in lexeme_values:
        # put the lexeme in the dictionaries
        cur_value = start_dict.setdefault(lexeme, set())
        if cur_value is None:
            start_dict[lexeme] = cur_value = set()
        cur_value.add(value)
        end_dict[lexeme] = cur_value
        #put beginning strings in the dictionary
        lex_start = ''
        for segment in lexeme[:-1]:
            lex_start += segment
            start_dict.setdefault(lex_start, None)
        #put ending strings in the dictionary
        lex_end = ''
        for segment in reversed(lexeme[1:]):
            lex_end = segment + lex_end
            end_dict.setdefault(lex_end, None)

def make_start_end_dicts_old(lexeme_values):
    """Return a dictionary of starting phrases and ending phrases of the lexemes.
    If a character sequence occurs as the start/end of a lexical entry but not as
    a lexical entry then it is in the dictionary with value None. If a character
    sequence occurs as a lexical entry (regardless of whether it also occurs
    at the start of another lexical entry) then its value is a list of possible
    ids. 
    
    @param lexeme_vals: dictionary of sets of values indexed by lexemes
    @type lexeme_vals: dictionary
    @return: dictionary of valid segments and initial portions of valid 
        segments. If the segment is valid it has a value. Initial portions 
        of valid segments are in the dictionary with the value None.
        Thus if 'abcd' is the valid segment with value 42 then the dictionary is
        {'abcd': 42, 'abc': None, 'ab': None, 'a': None}
        if 'ab' is also a valid segment with value 23 then the dictionary is
        {'abcd': 42, 'abc': None, 'ab': 23, 'a': None}
    @rtype: dictionary
    """
    start_dict = dict()
    end_dict = dict()
    for lexeme, value in lexeme_vals.items():
        if value is None:
            raise ValueError('value of lexeme %s cannot be None' % lexeme)
        lexstart = ''
        lexstart_list = list(lexeme)[:-1]
        for segment in lexstart_list:
            lexstart += segment
            try:
                val = start_dict[lexstart]
            except KeyError:
                start_dict[lexstart] = None
        try:
            val = start_dict[lexeme]
        except KeyError:
            start_dict[lexeme] = value
        else:
            if val:
                # shouldn't happen
                raise ValueError('lexeme %s, value %s' % (lexeme, repr(value)))
            else:
                start_dict[lexeme] = value
        lexend = ''
        lexend_list = list(reversed(lexeme))[:-1]
        for segment in lexend_list:
            lexend = segment + lexend
            try:
                val = end_dict[lexend]
            except KeyError:
                end_dict[lexend] = None
        try:
            val = end_dict[lexeme]
        except KeyError:
            end_dict[lexeme] = value
        else:
            if val:
                # shouldn't happen
                raise ValueError('lexeme %s, value %s' % (lexeme, repr(value)))
            else:
                end_dict[lexeme] = value
    return (start_dict, end_dict)

def match_from_start(s, start_dict):
    """"return the value of the longest phrase at the start of s.
    
    @param s: 
    @type s: string
    @param start_dict: 
    @type start_dict: dictionary
    @return: the value of the longest phrase at the start of s. 
        If no match is found then the tuple (None, None) is returned
    @rtype: tuple
    """
    last_match = last_entry_value = None
    p = ''
    for c in s:
        p += c
        try:
            value = start_dict[p]
            if value is not None:
                # keep track of last real entry
                last_match = p
                last_entry_value = value
        except KeyError:
            break
    return (last_match, last_entry_value)
    
def match_from_end(s, end_dict):
    """"return the value of the longest phrase at the end of s.
    
    @param s: 
    @type s: string
    @param end_dict: 
    @type end_dict: dictionary
    @return: the value of the longest phrase at the end of s. 
        If no match is found then the tuple (None, None) is returned
    @rtype: tuple
    """
    last_match = last_entry_value = None
    p = ''
    for c in reversed(s):
        p = c + p
        try:
            value = end_dict[p]
            if value is not None:
                # keep track of last real entry
                last_match = p
                last_entry_value = value
        except KeyError:
            break
    return (last_match, last_entry_value)
    
def maximal_match_old(s, start_dict):
    """"return the value of the longest phrase at the start of s.
    
    @param s: 
    @type s: string
    @param start_dict: 
    @type start_dict: dictionary
    @return: the value of the longest phrase at the start of s. 
        If no match is found then the tuple (None, None) is returned
    @rtype: tuple
    """
    last_match = last_entry_value = None
    for end in range(1, len(s)+1):
        p = s[0:end]
        try:
            value = start_dict[p]
            if value:
                # keep track of last real entry
                last_match = p
                last_entry_value = value
        except KeyError:
            break
    return (last_match, last_entry_value)

def test():
    sgmtr = MaximalMatch()
    sgmtr.add_segment_values((('bcd', 1), ('efg', 2)))
    ans = sgmtr.match_start('abcdefg')

if __name__ == "__main__":
    test()
