#
#   ListProjects
#
#   List the Fieldworks projects on this system.
#

from flexlibs import FLExInitialize, FLExCleanup
from flexlibs import AllProjectNames

#----------------------------------------------------------------


if __name__ == "__main__":

    FLExInitialize()

    print("\n".join(AllProjectNames()))
    
    FLExCleanup()
