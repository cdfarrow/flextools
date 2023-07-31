#
#   Project: FlexTools
#   Module:  FLExTools
#   Platform: .NET v2 Windows.Forms (Python.NET 2.7)
#
#   The main entry point for the FlexTools application is here as main().
#   It is called from the launcher application in 
#   FlexTools\scripts\RunFlexTools.py.
#
#   First, set up the following:
#        - logging
#        - configuration parameters and paths (flextools.ini)
#        - load flexlibs and handle any errors
#   Then, in main()
#        - initialise the Flex interface (flexlibs)
#        - launch the FlexTools UI
#
#   Copyright Craig Farrow, 2010 - 2022
#

import sys
import os
import traceback


# -----------------------------------------------------------
# Imports
# -----------------------------------------------------------

# This call is required to initialise the threading mode for COM calls
# (e.g. using the clipboard) It must be made before clr is imported.
import ctypes
ctypes.windll.ole32.CoInitialize(None)


import clr
import System

clr.AddReference("System.Windows.Forms")
from System.Windows.Forms import Application
from System.Windows.Forms import (
        MessageBox, 
        MessageBoxButtons, 
        MessageBoxIcon)

# -----------------------------------------------------------
# Logging
# -----------------------------------------------------------

import logging

if "DEBUG" in sys.argv[1:]:
    loggingLevel = logging.DEBUG
else:
    loggingLevel = logging.INFO

logging.basicConfig(filename='flextools.log', 
                    filemode='w', 
                    level=loggingLevel)

logger = logging.getLogger(__name__)


# -----------------------------------------------------------
# Paths and configuration
# -----------------------------------------------------------

from .. import version
logger.info(f"FLExTools library version: {version}")

from .FTConfig import FTConfig

#----------------------------------------------------------- 
# flexlibs
#----------------------------------------------------------- 

from .. import MinFWVersion, MaxFWVersion

try:
    from flexlibs import FLExInitialize, FLExCleanup

except Exception as e:
    msg = f"There was an issue during initialisation.\n{e}\n" \
          f"(This version of FLExTools has been tested with Fieldworks versions {MinFWVersion} - {MaxFWVersion}.)\n" \
          f"See flextools.log for more details."
    logger.error(msg)
    MessageBox.Show(msg,
                    "FLExTools: Fatal Error",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Exclamation)
    logger.error("Fatal exception importing flexlibs:\n%s" % traceback.format_exc())
    sys.exit(1)

logger.info(f"flexlibs imported successfully")


#----------------------------------------------------------- 
# UI
#----------------------------------------------------------- 

from .UIMain import FTMainForm

mainForm = None
# ------------------------------------------------------------------
def main(appTitle=None, customMenu=None, statusbarCallback=None):
    """
    Parameters:
        appTitle - a string with the name and version to display in 
            the main title bar. This allows systems built on FlexTools 
            to supply a custom title.
        customMenu - a tuple defining a custom menu that is inserted
            before the Help menu:
                (Menu Title, Menu Items)
                    Menu Title is a string
                    Menu Items is a list of tuples:
                        (Handler, Menu Text, Shortcut, Tooltip)
                    Handlers are functions that take two parameters, 
                    sender and event. 
                    If the Handler is None, then the menu is disabled.
                    Menu Text and Tooltip are strings.
                    Shortcut is a System.Windows.Forms.Shortcut sub-value,
                    or None.
                    If the tuple is None, then a separator is inserted.
        statusbarCallback - a function that returns a string to be
            included in the status bar.
        
    """
    global FTConfig
    global mainForm

    FLExInitialize()

    logger.debug("Creating MainForm")
    mainForm = FTMainForm(appTitle, customMenu, statusbarCallback)
    logger.debug("Launching WinForms Application")
    Application.Run(mainForm)

    # Save the configuration
    FTConfig.save()
    
    FLExCleanup()
    

def refreshStatusbar():
    global mainForm
    mainForm.UpdateStatusBar()
