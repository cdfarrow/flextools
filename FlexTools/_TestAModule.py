#
#   _TestAModule
#
#   Test frame for developing a new Module. Run as a command-line application:
#   ..\py_net.bat _TestAModule.py
#

import sys
sys.path.append ("..\FLExLibs")
sys.path.append ("Modules")
sys.path.append ("Modules\Chinese")

from FLExDBAccess import FLExDBAccess, FDA_DatabaseError
import FTReport

#---------------------------------
# Module to test
from Update_Reversal_Sort_Fields import FlexToolsModule

#---------------------------------

# Configurables:
FLExDBName           = "Parser-experiments"
#----------------------------------------------------------------


# If your data doesn't match your system encoding (in the console) then
# redirect the output to a file: this will make it utf-8.
## BUT This doesn't work in IronPython!!
import codecs
if sys.stdout.encoding == None:
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout)


#----------------------------------------------------------------

FlexDB = FLExDBAccess()

try:
    # No name opens the first db on the default server
    FlexDB.OpenDatabase(dbName = FLExDBName, verbose = True)
except FDA_DatabaseError, e:
    print "FDO Cache Create failed!"
    print e.message
    sys.exit(1)
    
# Module Init
FlexToolsModule.Help()

reporter = FTReport.FTReporter()
FlexToolsModule.Run(FlexDB, reporter)
print reporter.messageCounts
for m in reporter.messages:
    print m
    
    

