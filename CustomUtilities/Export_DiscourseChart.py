# -*- coding: cp1252 -*-

# Export_DiscourseChart.py
#
# Demonstrating access to the DiscourseChart data in a FieldWorks project.
#
# Craig Farrow
# July 2008
#
# Platforms: Python .NET and IronPython
#
# TODO -- Get this actually working with real data

from FLExDBAccess import FLExDBAccess

from SIL.FieldWorks.Common.COMInterfaces import ITsString, ITsStrBldr

# If your data doesn't match your system encoding (in the console) then
# redirect the output to a file: this will make it utf-8.
## BUT This doesn't work in IronPython!!
import codecs
import sys
if sys.stdout.encoding == None:
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout)


#============ The Database ===============

FlexDB = FLExDBAccess()

# No name opens the first db on the default server
if not FlexDB.OpenDatabase(dbName = "", verbose = True):
    print "FDO Cache Create failed!"
    sys.exit(1)
       
#============== Discourse Data ===============

# From Steve Miller 21 Apr 2008 (FLEx List)

    
discdata = FlexDB.lp.DiscourseDataOA
print 'Discourse Data:'
print


print "Text Chart Markers:"
for li in FlexDB.UnpackNestedPossibilityList(discdata.ChartMarkersOA.PossibilitiesOS, True):
    print li

for li in FlexDB.UnpackNestedPossibilityList(ConstChartTemplOA.PossibilitiesOS, True):
    print li

for chart in discdata.ChartsOC :
    basetext = chart.BasedOnRA
    print
    print ITsString(basetext.ChooserNameTS).Text
    if not "Wide river" in ITsString(basetext.ChooserNameTS).Text:
        print "Skipping..."
        continue
    print

    # Print the Baseline text
    for paragraph in basetext.ParagraphsOS :

        # The text (contents) of a paragraph is formatted
        # with embedded characters, to tell the program
        # how to format it for display. In other words,
        # it is a "TsString".
        

        # A paragraph is composed of one or more lengths
        # of text called a "run".

        contents = paragraph.Contents
        print contents.Text

    print

    # Print the Discourse chart
##    print dir(chart)
    for i, row in enumerate(chart.RowsRS):
        print dir(row)
        print "Row:", i
        agent = row.SourceRA
        if agent:
            print "[Agent]", agent.Name
        
        rowtext = row.TextOA
        print "[Rowtext]", rowtext


