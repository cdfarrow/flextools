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

"""demonstration of chinese, pinyin checking code."""

from __future__ import unicode_literals
from __future__ import print_function

from check_pinyin import init_chin_sgmtr
from check_pinyin import check_pinyin as check_tonenum

# utf8 encoded text files with one word per line
# each line has chinese a tab and then tonenum
dict_fname="xhc4_words.txt"
dict_supp="laibin_chin_supp.txt"

tests = (
    ('坳', 'ao4'),
    ('敷草药', 'fu1 cao3yao4'),
    ('敷草药', 'fu1cao3yao4'),
    ('失利的仗', 'shi1//li4 .de5 zhang4'),
    ('失利的仗', 'shi1//li4 .de5 zhang4 de5'),
    ('人民公园', 'ren2'),
    ('同仁小区', 'ren2'),
    ('民和路', 'min2 he2|he4|hu2|huo2|huo4 lu4'),
)


chin_sgmtr = init_chin_sgmtr((dict_fname, dict_supp))

errors = list()
for chin, tonenum in tests:
    errors += check_tonenum(chin_sgmtr, chin, tonenum)
print('\n'.join(errors))
