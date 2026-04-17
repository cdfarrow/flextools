#
#   test_ChineseUtilities.py
#
#   Craig Farrow
#   Aug 2023
#
#   A pytest suite for testing the ToneNumber and SortString generator 
#   functions of ChineseUtilities.py
#

import pytest
from ChineseUtilities import ChineseParser, SortStringDB

#----------------------------------------------------------- 

test_data = [
    ('路', 'lu4', 'lu4AC2512121354251'),
    ('你好', 'ni3 hao3', 'ni3@G3235534;hao3@F531551'),
    ('中国话', 'Zhong1guo2hua4', 'zhong1@D2512;guo2@H25112141;hua4@H45312251'),
    ('枣红色', 'zao3hong2 se4', 'zao3@H12523444;hong2@F551121;se4@F355215'),
    ('录音', 'lu4//yin1', 'lu4@H51154134;yin1@I414312511'),
    ('绿', 'lu:4', 'lu94AA55151124134'),
    ('乱', 'luan4', 'luan4@G3122515'),
    ('耳朵', 'er3.duo5', 'er3@F122111;duo5@F351234'),
    ('孩子', 'hai2.zi5', 'hai2@I551415334;zi5@C551'),
    ('撒谎', 'sa1//huang3', 'sa1AE151122125113134;huang3AA45122415325'),
    ('老老实实地', 'lao3lao5shi2shi2 .de5',
        'lao3@F121335;lao5@F121335;shi2@H44544134;shi2@H44544134;de5@F121525'),
    ('去人民公园', 'qu4 ren2min2 gong1yuan2',
        'qu4@E12154;ren2@B34;min2@E51515;gong1@D3454;yuan2@G2511351'),
    ('座儿', 'zuor4', 'zuo4A@4133434121;er2@B35'),
    ('叭儿狗', 'bar1gou3', 'ba1@E25134;er2@B35;gou3@H35335251'),
    ('白眼儿狼', 'bai2yanr3lang2',
        'bai2@E32511;yan3AA25111511534;er2@B35;lang2A@3534511534'),
    ('卡拉OK', 'ka3la1ou1kei4', 'ka3@E21124;la1@H15141431;ou1II;kei4II'),
    ('你在？', 'ni3 zai4?', 'ni3@G3235534;zai4@F132121;?'),
    ('老（人）', 'lao3 (ren2)', 'lao3@F121335;(;ren2@B34;)'),
    ('他/她/它', 'ta1/ta1/ta1', 'ta1@E32525;/;ta1@F531525;/;ta1@E44535'),
    ('1单数', '1 dan1shu4', '1;dan1@H43251112;shu4AC4312345313134'),
    ('左…右…', 'zuo3…you4…', 'zuo3@E13121;…;you4@E13251;…'),
    ('；', ';', ';'),
    ('连…也', 'lian2…ye3', 'lian2@G1512454;…;ye3@C525'),
    ('红', 'gong1|hong2', None),
 
    # Ambiguous parses don't work with punctuation
    #('是（1单）',   "shi4 (1 dan1)", 'shi4@I251112134;(;1;dan1@H43251112;)'),

    # Passes PY check, but fails Sort String due to angle brackets
    # not being included in chin_utils.tonenum_syl_pat
    #('\N{LEFT DOUBLE ANGLE BRACKET}做\N{RIGHT DOUBLE ANGLE BRACKET}', "<<zuo4>>", None),
]

# Error cases
test_data_fail = [
    # Wrong number of syllables
    ("录音机",    "lu4yin1",       '[Expected "lu4yin1ji1"]'),
    
    # Wrong tone
    ("中国",      "zhong1 guo4",  '[Expected "zhong1|zhong4 guo2"]'),
]

#----------------------------------------------------------- 

@pytest.fixture(scope="module")
def parser():
    return ChineseParser()


@pytest.fixture(scope="module")
def sorter():
    return SortStringDB()


@pytest.mark.parametrize("chns, tonenum, _", test_data)
def test_tonenum(parser, chns, tonenum, _):
    result = parser.Tonenum(chns, tonenum)

    # result is None if the tonenum is correct, 
    # otherwise it's an error message.
    assert not result, f"Tonenum failed for {chns!r}: {result}"


@pytest.mark.parametrize("chns, tonenum, sortstring", test_data)
def test_sort_string(sorter, chns, tonenum, sortstring):
    # Can't generate a sort string with unresolved ambiguities.
    if '|' in tonenum: return
    
    result = sorter.SortString(chns, tonenum)

    assert result == sortstring, f"SortString error for {chns!r}: {result!r}"


@pytest.mark.parametrize("chns, tonenum, message", test_data_fail)
def test_tonenum_fails(parser, chns, tonenum, message):
    result = parser.Tonenum(chns, tonenum)

    # These ones fail and should report the given message.
    assert result == message, f"Tonenum for {chns!r} gave error {result!r} instead of {message!r}"

