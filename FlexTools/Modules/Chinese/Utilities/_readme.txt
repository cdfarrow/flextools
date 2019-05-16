Chinese Tools Utilities
=======================

June 2011

This directory contains Python utility scripts for managing the Chinese
data files. The datafiles are stored in ..\Lib\Datafiles.

Data files
----------

xhc4_words.txt

	A mapping of words to Pinyin (tab separated) according to the 
	Xiandai Hanyu Cidian formatting.

char_dat.pkl

	A Python pickle of a Python dictionary mapping individual
	Chinese characters to their possible Pinyin forms, plus
	stroke information for generating a sort keys.
    	Data is [chr, pinyin, # strokes, strokes]

qryExportBasicVocab.utf8.txt (in Archive dir)

	A Chinese dictionary with defintions from Dan Edwards
	including Pinyin in tone-number and 'tone-spell' formats.
	(This file isn't used by any of these tools, so is omitted
	from the user distribution.)


Utilities
---------

check_dict_vs_sort.py

	Checks that all characters in the dictionary file (xhc4_words.txt)
	are included in the character data (char_dat.pkl)

edit_sort_pickle.py

	Loads the char_dat.pkl file and provides a few functions for 
	editing the file and saving it again. Run with interactive shell.

extract_pkl2sort.py

	Writes the character sort data (char_dat.pkl) to a file (ch2sort.txt)
	for use in generating sort keys. The output file is:
	<character> [<tab> <pinyin> <tab> <sort-string>]+
	Currently the ch2sort file is not used by these utilities, but it
	is a human-readable format.

