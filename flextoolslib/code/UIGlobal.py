#
#   Project: FlexTools
#   Module:  UIGlobal
#
#   Global settings, etc., for the FLExTools UI
#
#   Craig Farrow
#   Oct 2009-2019
#

import clr
clr.AddReference("System")
clr.AddReference("System.Drawing")
clr.AddReference("System.Windows.Forms")

import os
import System
from System.Drawing import (Color,
                            Font, FontStyle, FontFamily)

# Icon path details

ICON_PATH0      = os.path.join(os.path.dirname(__file__), "__icons\\")
ICON_PATH1      = os.path.join(ICON_PATH0, "IconBuffet Redmond Studio\\")
ICON_SUFFIX1    = "_16.gif"
ICON_PATH2      = os.path.join(ICON_PATH0, "Fugue\\")
ICON_SUFFIX2    = ".png"

ApplicationIcon   = ICON_PATH0 + "flextools.ico"
ModuleIcon        = ICON_PATH0 + "module.ico"
ToolbarIconParams = (ICON_PATH1, ICON_SUFFIX1)
ReportIconParams  = (ICON_PATH2, ICON_SUFFIX2)

# General appearance

SPLITTER_WIDTH = 4

# Font styles
smallFont   = Font(FontFamily.GenericSansSerif, 8.0)
normalFont  = Font(FontFamily.GenericSansSerif, 10.0)
headingFont = Font(FontFamily.GenericSansSerif, 11.0)

# Colours
leftPanelColor  = Color.FromArgb(0xFA, 0xF8, 0xF0) # Light wheat
rightPanelColor = Color.FromArgb(0xFF, 0xFA, 0xE8) # Light cream
helpDialogColor = Color.White
