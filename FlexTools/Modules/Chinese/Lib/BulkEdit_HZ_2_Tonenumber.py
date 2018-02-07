# -*- coding: utf-8 -*-
#
#   BulkEdit_HZ_2_Tonenumber
#    - A Fieldworks Writing System transducer
#
#
#   C D Farrow
#   June 2011
#
#

"""
Produces Pinyin tone number from Chinese (Hanzi) as follows:

 - Numerals 1-5 at the end of the Pinyin pronunciation for tones 1-4 plus
 nuetral tone ('5'), e.g. 'hai2.zi5'

 - u-diaresis is represented with a colon (':') at the end of the syllable
 and before the tone number, e.g. lu:4se4.

Following the Pinyin formatting in Xian Dai Han Yu Ci Dian (现代汉语词典),
the tone number field also has spaces in specific places and special
punctuation between certain syllables, e.g. 'lu4//yin1', 'jiao3.zi5'.

Ambiguities in the Pinyin are included as a list of possibilities
separated by a vertical bar '|', e.g. 'zhong1|zhong4'.

""" 

import site
site.addsitedir(r"Lib")

from ChineseUtilities import ChineseParser

                 
#----------------------------------------------------------------
# The main processing function

def Convert(hz):

    Parser = ChineseParser()
    return Parser.Tonenum(hz)
