# -*- coding: utf-8 -*-
#
#   BulkEdit_Tonenumber_2_Pinyin
#    - A Fieldworks Writing System transducer
#
#
#   C D Farrow
#   June 2011
#
#

"""
Generates diacritic Pinyin from tone number Pinyin.

If the tone number has any unresolved ambiguities or problems
(indicated by '|' or '[') in the tone number field,
then the output will be blank.
"""


from ChineseUtilities import TonenumberToPinyin

                 
#----------------------------------------------------------------
# The main processing function

def Convert(tonenum):

    if '|' in tonenum or '[' in tonenum: 
        return u""
    
    return TonenumberToPinyin(tonenum)
