#----------------------------------------------------------------------------
# Name:         __init__.py
# Purpose:      flextools is a GUI tool for running Python scripts on 
#               FieldWorks Language Explorer projects.
#----------------------------------------------------------------------------

version = "2023.3.16"

# Minimum and maximum supported versions of Fieldworks
# (Later versions should work if the LCM interface hasn't changed.)
MinFWVersion = "9.0.4"
MaxFWVersion = "9.1.18"


#----------------------------------------------------------------------------
# Define exported classes, etc. at the top level of the package

# The main application
from .code.FLExTools import (
    main, 
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

# Give access to the FlexTools configuration values, especially 
# for currentProject
from .code.FTConfig import (
    FTConfig
    )
    
# Expose RunModule for testing purposes (see TestAModule.py)
from .misc.RunModule import (
    RunModule, 
    )
