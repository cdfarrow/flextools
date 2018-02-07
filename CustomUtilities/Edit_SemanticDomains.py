# -*- coding: cp1252 -*-


# The Path is supplied by FlexLibs.pth in the Site-packages directory
# with a single line pointing to the FlexLibs directory (Python.NET only)
from FLExDBAccess import FLExDBAccess

# If your data doesn't match your system encoding (in the console) then
# redirect the output to a file: this will make it utf-8.
# NOTE This does not work in IronPython!!
import codecs
import sys
if sys.stdout.encoding == None:
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout)


#============ Open the database ===============

FlexDB = FLExDBAccess()

# No name opens the first db on the default server
if not FlexDB.OpenDatabase(dbName = "", verbose = True):
    print "FDO Cache Create failed!"
    sys.exit(1)
       


# Semantic Domains
#
# From Ken Zook - 8 Sep 2008
#
# HVOs are unique to a single database and will not persist between a
# dump and a reload. They are not dumped to XML at all. For a unique id
# for an object that does persist in the XML file and thus restored in
# a load process, you should use the GUID associated with each object
# instead of the id. The GUID comes from guid$ in the CmObject table.
# It is stored as the ID attribute in an XML dump. Guids for some lists
# are maintained across all databases while some other lists are unique
# to a single database. 
# The Guids for semantic domains are maintained across all databases.
# To use the Guids in a dump file you would use
# <Link target="ID60FAF11-CC6E-48DB-8A13-82F86D78AB00"/>
# In the dump file we prepend uppercase I to each guid to ensure it
# is a valid XML id (can’t start with a digit).

  
print "Semantic Domains:"

#print help(FlexDB.GetAllSemanticDomains)
for i in FlexDB.GetAllSemanticDomains(True):
    print i.Hvo, i

print


limit = 10

print "Lexicon contains", FlexDB.LexiconNumberOfEntries(), "entries.",
print "( Listing up to", limit, ")"
print

for e in FlexDB.LexiconAllEntries():
    print "\lx", FlexDB.LexiconGetLexemeForm(e)
    for sense in e.SensesOS :
        print "\ge", FlexDB.LexiconGetSenseGloss(sense)
        print "\pos", FlexDB.LexiconGetSensePOS(sense)
        print "\def", FlexDB.LexiconGetSenseDefinition(sense)
        print "\is", sense.SemanticDomainsRC.Count
        for i in sense.SemanticDomainsRC.ToList():
            print i, i.Hvo      # Display string, Hvo
        ### CHANGES the DB: Can use either Hvo or the Object itself.
        ###                 Can also add a list of Hvos or Objects.
        ##sense.SemanticDomainsRC.Add(3902) # eg == 4 - Social behavior
        ##sense.SemanticDomainsRC.Add(semDomObject) # eg == 6 Work
        
    print

    if limit > 0: limit -= 1
    else:         break

