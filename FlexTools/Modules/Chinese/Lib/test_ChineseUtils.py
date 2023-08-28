# -*- coding: utf-8 -*-
#
#   test_ChineseUtilities
#
#   Craig Farrow
#   Aug 2023
#
#   Run some sample Chinese and Pinyin data through the ToneNumber and 
#   SortString generator functions.
#


from ChineseUtilities import ChineseParser, SortStringDB


# --- Testing ---

testSet = [
           ("路",        "lu4"),
           ("你好",       "ni3 hao3"),
           ("中国话",      "Zhong1guo2hua4"),
           ('枣红色',      "zao3hong2 se4"),   # Ambiguous parse
           ("录音",       "lu4yin1"),
           ("绿",        "lu:4"),            # Multiple pronunciations
           ("乱",        "luan4"),
           ("耳朵",       "er3.duo5"),
           ("孩子",       "hai2.zi5"),
           ("撒谎",       "sa1//huang3"),
           ("老老实实地",   "lao3lao5shi2shi2 .de5"),
           ("去人民公园",    ""),                # Generate the Pinyin

           # er hua is handled
           ('\u5ea7\u513f', 'zuor4'),
           ('\u53ed\u513f\u72d7', 'bar1gou3'),
           ('\u767d\u773c\u513f\u72fc', 'bai2yanr3lang2'),
           # Latin letters
           ('\u5361\u62c9OK', 'ka3la1ou1kei4'),

           # This is okay
           ("你在\N{FULLWIDTH QUESTION MARK}", "ni3 zai4?"),

           # Other punctuation is supported
           ('老（人）', "lao3 (ren2)"),
           ('他，她，它', 'ta1, ta1, ta1'),
           ('他/她/它', 'ta1/ta1/ta1'),
           ('1单数', "1 dan1shu4"),
           ('左…右…', 'zuo3…you4…'),
           ('\N{FULLWIDTH SEMICOLON}', ';'),
           ('连\N{HORIZONTAL ELLIPSIS}也', 'lian2…ye3'),

           # Purposeful pinyin errors
           ("录音机",    "lu4yin1"),    
           ("中国",      "zhong1 guo4"), 

           # Fails PY check because the combination of ambiguous pinyin
           # is checked by check_pinyin.check_pinyin() and that
           # function doesn't handle punctuation
           ("你好吗\N{FULLWIDTH QUESTION MARK}", "ni3 hao3 .ma5?"),
           ('是（1单）', "shi4 ( 1 dan)"),

           # Passes PY check, but fails Sort String due to angle brackets
           # not being included in chin_utils.tonenum_syl_pat
           ('\N{LEFT DOUBLE ANGLE BRACKET}做\N{RIGHT DOUBLE ANGLE BRACKET}', "<<zuo4>>"),

           # Ambiguities
           ('红',       "gong1|hong2"),
           ]


print("--- Testing Chinese Parser and Sort String Generator ---")
Parser = ChineseParser()
Sorter = SortStringDB()
for chns, tonenum in testSet:
    print("%s [%s] %s" % (chns, repr(chns), tonenum))
    #print "\tParse:\t", Parser.Tonenum(chns, tonenum)
    #if tonenum:
    print("\tCheck:\t", tonenum)
    result = Parser.Tonenum(chns, tonenum)
    print("\t\t", result if result else "OK")
    ss = Sorter.SortString(chns, tonenum)
    print("\tSort:\t", ss)
