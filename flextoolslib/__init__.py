#----------------------------------------------------------------------------
# Name:         __init__.py
# Purpose:      flextools is a GUI tool for running Python scripts on 
#               FieldWorks Language Explorer projects.
#----------------------------------------------------------------------------

version = "2022.12.0"

# Minimum and maximum supported versions of Fieldworks
# (Later versions should work if the LCM interface hasn't changed.)
MinFWVersion = "9.0.4"
MaxFWVersion = "9.1.16"


# Define exported classes, etc. at the top level of the package

# The main application
from .code.FLExTools import (
    main, 
    )

# The full paths to the config file (flextools.ini), and the Modules and 
# Collections folders.
from .code.FTPaths import (
    CONFIG_PATH,
    MODULES_PATH,
    COLLECTIONS_PATH,
    )
    
# The Modules class and documentation constants
from .code.FTModuleClass import (
    FlexToolsModuleClass, 
    FTM_Name,
    FTM_Version,
    FTM_ModifiesDB,
    FTM_Synopsis,
    FTM_Help,
    FTM_Description,
    )

from .misc.RunModule import (
    RunModule, 
    )
