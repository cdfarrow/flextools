#----------------------------------------------------------------------------
# Name:         __init__.py
# Purpose:      flextools is a GUI tool for running Python scripts on 
#               FieldWorks Language Explorer projects.
#----------------------------------------------------------------------------

version = "2.2.0a"

# Define exported classes, etc. at the top level of the package

from .code.FLExTools import (
    main, 
    )

from .code.FTModuleClass import (
    FlexToolsModuleClass, 
    FTM_Name,
    FTM_Version,
    FTM_ModifiesDB,
    FTM_Synopsis,
    FTM_Help,
    FTM_Description,
    )
