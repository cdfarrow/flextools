#
#   makezip.py
#
#   Package the FlexTools folder into a zip file for distribution.
#
#   Copyright Craig Farrow, 2022
#

import sys
sys.path.append("FlexTools/scripts/")

from Version import Version

import pathlib
from zipfile import ZipFile, ZIP_DEFLATED


# FlexTools\ contains the following files that we need to package up:
#   - .vbs, .bat & .py scripts, including the scripts\ folder
#   - flextools.ini - a default configuration
#   - Modules and Collections folders
#   

FTPath = pathlib.Path("FlexTools")

ZIPFILE_NAME = f"dist\\FlexTools_{Version}.zip"

PATH_PATTERNS = (
    "*.vbs",
    "scripts/*",
    "Modules/**/*",     # "**" = recursive
    "Collections/*",
    )
    
FILTERED_SUFFIXES = (".pyd", ".pyc", ".bak", ".log", ".doc", ".tmp")

#----------------------------------------------------------- 

def includeFile(path):
    if path.stem == "__pycache__":           
        return False
    # Filter out the Archive folder in the Chinese modules
    if path.name == "Archive":   
        return False
    if path.is_file() and path.parent.name == "Archive":   
        return False
    
    return not path.suffix in FILTERED_SUFFIXES


print (f"Creating archive {ZIPFILE_NAME}")

with ZipFile(ZIPFILE_NAME, 'w', ZIP_DEFLATED) as z:
    for pathPattern in PATH_PATTERNS:
        for fn in filter(includeFile, FTPath.glob(pathPattern)):
            print(f"adding '{fn}'")
            z.write(fn)

