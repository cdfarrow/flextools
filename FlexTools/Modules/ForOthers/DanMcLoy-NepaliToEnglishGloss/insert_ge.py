# Inserts a \ge field after every \d_nep field that contains
# a word glossed in nep_en_gloss.txt
# WARNING:  ANY EXISTING \ge FIELDS WILL BE DELETED!!!!


# Settings
nepFld = 'd_nep'    # Input field that contains Nepali.  (Not necessarily unique.) 
enFld = 'ge'        # Output field that will contain English
glossFile = 'nep_en_gloss.txt'  # File containing mapping of Nepali to English


import codecs
import re

def devEssence(s):
    """Given a Devanagari input string (Unicode), returns a simplified form in which
    phonologically insiginicant differences are standardized."""
    s = re.sub(u'इ', u'ई', s)
    s = re.sub(u'उ', u'ऊ', s)
    s = re.sub(u'ि', u'ी', s)
    s = re.sub(u'ु', u'ू', s)
    s = re.sub(u'श', u'स', s)
    s = re.sub(u'ष', u'स', s)
    s = re.sub(ur'[- \u200C\u200D]', '', s)
    return s

# Read glosses file
f = codecs.open(glossFile, encoding='utf-8')
geDict = dict()
for line in f:
    m = re.search(r'(.+)\t(.+)', line)
    if (m):
        ge = m.group(2)
        de = devEssence(m.group(1))
        if de in geDict:
            geDict[de] += " / " + ge
        else:
            geDict[de] = ge
print "Loaded", len(geDict), "glosses...\n"
f.close()


# SFM files to process
infileName = 'Lhomi Dictionary Project-sfm.txt'
outfileName = 'out.txt'

# Process SFM files
infile = codecs.open(infileName, encoding='utf-8')
outfile = codecs.open(outfileName, encoding='utf-8', mode='w+')
ct = 0
ctTry = 0
for line in infile:
    m = re.match(ur'\\'+nepFld+ur"\s+(\S.*)", line.strip("\r\n"))   #***
    if (m):
        de = devEssence(m.group(1))
        ctTry += 1
        if de in geDict:
            outfile.write(line)
            outfile.write(u"\\" + enFld + ' ' +geDict[de] + "\n")   #***
            ct += 1
        else:
            outfile.write(line)
    else:
        m = re.match(ur'\\'+enFld+ur"\s+(\S.*)", line)
        if (m):
            # Don't output original ge field.
            print "Deleting original \\", enFld, "field: ", m.group(1)
        else:
            outfile.write(line)
print "Processed", ctTry, "\\" + nepFld + " fields.\nMatched and inserted", ct, "glosses."

infile.close()          #***
outfile.close()         #***



