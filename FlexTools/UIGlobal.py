#
#   Project: FlexTools
#   Module:  UIGlobal
#
#   Global settings etc for UI
#
#   Craig Farrow
#   Oct 2009
#   v0.00
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

ICON_PATH0      = os.path.join(os.path.dirname(__file__), u"__icons\\")
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
smallFont   = Font(FontFamily.GenericSansSerif, 8)
normalFont  = Font(FontFamily.GenericSansSerif, 10)
headingFont = Font(FontFamily.GenericSansSerif, 11)

# Colours
rightPanelColor = Color.LightYellow
leftPanelColor = Color.AliceBlue
helpDialogColor = Color.White
