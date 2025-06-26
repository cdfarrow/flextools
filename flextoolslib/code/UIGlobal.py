#
#   Project: FlexTools
#   Module:  UIGlobal
#
#   Global settings, etc., for the FLExTools UI
#
#   Craig Farrow
#   Oct 2009-2022
#

import clr
clr.AddReference("System")
clr.AddReference("System.Drawing")
clr.AddReference("System.Windows.Forms")

import os
import System
from System.Drawing import (Color,
                            Size,
                            Font, FontStyle, FontFamily)
from sys import argv

# Icon path details

ICON_PATH0      = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                               "icons")
ICON_PATH1      = os.path.join(ICON_PATH0, "IconBuffet Redmond Studio")
ICON_SUFFIX1    = "_16.gif"
ICON_PATH2      = os.path.join(ICON_PATH0, "Fugue")
ICON_SUFFIX2    = ".png"

ApplicationIcon   = os.path.join(ICON_PATH0, "Flextools.ico")
ModuleIcon        = os.path.join(ICON_PATH0, "Module.ico")
ToolbarIconParams = (ICON_PATH1, ICON_SUFFIX1)
ReportIconParams  = (ICON_PATH2, ICON_SUFFIX2)

# General appearance

SPLITTER_WIDTH = 4

if "DEMO" in argv[1:]:
    # Font styles
    smallFont   = Font(FontFamily.GenericSansSerif, 12.0)
    normalFont  = Font(FontFamily.GenericSansSerif, 15.0)
    headingFont = Font(FontFamily.GenericSansSerif, 16.5)

    # Window sizes
    mainWindowSize = Size(900, 500)
    collectionsWindowSize = Size (800,500)

else:
    # Font styles
    smallFont   = Font(FontFamily.GenericSansSerif, 8.0)
    normalFont  = Font(FontFamily.GenericSansSerif, 10.0)
    headingFont = Font(FontFamily.GenericSansSerif, 11.0)

    # Window sizes
    mainWindowSize = Size(700, 500)
    collectionsWindowSize = Size (600,500)


# Colours
leftPanelColor  = Color.FromArgb(0xFA, 0xF8, 0xF0) # Light wheat
rightPanelColor = Color.FromArgb(0xFF, 0xFA, 0xE8) # Light cream
helpDialogColor = Color.White
