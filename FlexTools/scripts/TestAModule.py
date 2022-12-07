#
#   TestAModule
#
#   Test frame for developing a new Module. 
#   Run as a command-line application:
#       py TestAModule.py <Module> <Project>
#

import sys


LOG_FILE = "TestAModule.log"

import logging
logging.basicConfig(filename=LOG_FILE, 
                    filemode='w', 
                    level=logging.DEBUG)

logger = logging.getLogger(__name__)


from flextoolslib import RunModule
    

#----------------------------------------------------------------
def usage():
    print ("USAGE: TestAModule <Module> <Project>")

#----------------------------------------------------------------

if __name__ == "__main__":

    if len(sys.argv) != 3:
        usage()
        sys.exit(1)
        
    ModuleToTest = sys.argv[1]
    ProjectName  = sys.argv[2]

    if RunModule(ModuleToTest, ProjectName):
        print ("Success!")
    else:
        print ("Failed!")

    print (f"=== {LOG_FILE} ===")
    
    with open(LOG_FILE, 'r') as f:
        print(f.read()) 
