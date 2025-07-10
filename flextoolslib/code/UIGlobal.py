#
#   Project: FlexTools
#   Module:  UIGlobal
#
#   Global settings, etc., for the FLExTools UI
#
#   Craig Farrow
#   Oct 2009-2022
#


import os
from sys import argv

import clr
clr.AddReference("System.Drawing")

from System.Drawing import (Color,
                            Size,
                            Icon,
                            Font, FontStyle, FontFamily)

# --- Paths ---

BASE_PATH       = os.path.dirname(os.path.dirname(__file__))

LOCALES_PATH    = os.path.join(BASE_PATH, "locales")

# Icon path details

ICON_PATH0      = os.path.join(BASE_PATH, "icons")
ICON_PATH1      = os.path.join(ICON_PATH0, "IconBuffet Redmond Studio")
ICON_SUFFIX1    = "_16.gif"
ICON_PATH2      = os.path.join(ICON_PATH0, "Fugue")
ICON_SUFFIX2    = ".png"

ApplicationIconFile = os.path.join(ICON_PATH0, "Flextools.ico")
ApplicationIcon   = Icon(ApplicationIconFile)
ModuleIconFile    = os.path.join(ICON_PATH0, "Module.ico")
ToolbarIconParams = (ICON_PATH1, ICON_SUFFIX1)
ReportIconParams  = (ICON_PATH2, ICON_SUFFIX2)

# --- General appearance ---

SPLITTER_WIDTH = 4

if "DEMO" in argv[1:]:
    # Font styles
    smallFont   = Font(FontFamily.GenericSansSerif, 12.0)
    normalFont  = Font(FontFamily.GenericSansSerif, 15.0)
    headingFont = Font(FontFamily.GenericSansSerif, 16.5)

    # Window sizes
    mainWindowSizeNormal    = Size(1200,550)
    mainWindowSizeNarrow    = Size(900, 550)
    collectionsWindowSize   = Size(850, 500)
    moduleInfoSize          = Size(500, 500)
    projectChooserSize      = Size(400, 300)
    aboutBoxSize            = Size(600, 350)

else:
    # Font styles
    smallFont   = Font(FontFamily.GenericSansSerif, 8.0)
    normalFont  = Font(FontFamily.GenericSansSerif, 10.0)
    headingFont = Font(FontFamily.GenericSansSerif, 11.0)

    # Window sizes
    mainWindowSizeNormal    = Size(900, 500)
    mainWindowSizeNarrow    = Size(650, 500)
    collectionsWindowSize   = Size(650, 500)
    moduleInfoSize          = Size(400, 400)
    projectChooserSize      = Size(350, 250)
    aboutBoxSize            = Size(400, 250)

# Colours

leftPanelColor  = Color.FromArgb(0xFA, 0xF8, 0xF0) # Light wheat
rightPanelColor = Color.FromArgb(0xFF, 0xFA, 0xE8) # Light cream
helpDialogColor = Color.White

accentColor     = Color.DarkSlateBlue   # For text headings/accents

