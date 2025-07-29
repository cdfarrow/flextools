#
#   Project: FlexTools
#   Module:  FTDialogs
#   Platform: .NET Windows.Forms (Using python.NET 3)
#
#   General dialog functions for use by modules (e.g. for entering parameters
#   during a run.)
#
#   Copyright Craig Farrow
#   2025
#

from . import UIGlobal

from cdfutils.DotNet import (
    ChooserDialog,
    RadioDialog,
    TextDialog,
    )


# ------------------------------------------------------------------

def FTDialogChoose(title,
                   items, 
                   defaultItem=None):
        """
        Show a dialog with a dropdown menu for the user to choose from 
        a list of items.
        """

        dlg = ChooserDialog(title,
                            items,
                            defaultItem)

        dlg.Icon = UIGlobal.ApplicationIcon

        return dlg.Show()


def FTDialogRadio(title,
                  items, 
                  defaultItem=None):
        """
        Show a dialog with radio buttons for the user to choose from 
        a list of items.
        """

        dlg = RadioDialog(title,
                          items,
                          defaultItem)

        dlg.Icon = UIGlobal.ApplicationIcon

        return dlg.Show()


def FTDialogText(title,
                 defaultValue = ""):
        """
        Show a dialog for the user to enter a text value.
        """

        dlg = TextDialog(title,
                         defaultValue)

        dlg.Icon = UIGlobal.ApplicationIcon

        return dlg.Show()

