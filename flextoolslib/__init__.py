#----------------------------------------------------------------------------
# Name:         __init__.py
# Purpose:      FLExTools is a GUI tool for running Python scripts on 
#               FieldWorks Language Explorer projects.
# Architecture: The bulk of the FLExTools code resides in this library
#               (flextoolslib). The actual FLExTools launcher 
#               (RunFlexTools.py) simply calls flextoolslib.main()
#
#----------------------------------------------------------------------------

# We use the date of release for the version number: YYYY.M.D
version = "2025.8.26"

# Minimum and maximum supported versions of Fieldworks
# (Later versions should work if the LCM interface hasn't changed.)
MinFWVersion = "9.0.17"
MaxFWVersion = "9.3.1"


#----------------------------------------------------------------------------
# Define exported classes, etc. at the top level of the package

# The main application
from .code.FLExTools import (
    main, 
    refreshStatusbar,
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

from .code.FTDialogs import (
    FTDialogChoose,
    FTDialogRadio,
    FTDialogText,
    )
        
# Expose RunModule for testing purposes (see TestAModule.py)
from .misc.RunModule import (
    RunModule, 
    )
