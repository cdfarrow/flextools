#
#   Project: FlexTools
#   Module:  UISettings
#   Platform: .NET Windows.Forms (Using python.NET 3)
#
#   Settings dialog.
#
#   Copyright Craig Farrow
#   2025
#

from . import UIGlobal
from .FTConfig import FTConfig
from .FTDialogs import FTDialogChoose

from System.Windows.Forms import MessageBox
    
# ------------------------------------------------------------------

def Settings(sender=None, event=None):

    languages = sorted(UIGlobal.ALL_LOCALES.values())
    currentLanguge = UIGlobal.ALL_LOCALES[FTConfig.UILanguage]
    
    selected = FTDialogChoose(_("Select the UI language"),
                              languages,
                              currentLanguge)

    if selected and selected != currentLanguge:
        FTConfig.UILanguage = UIGlobal.LANGUAGE_TO_LOCALE[selected]
        MessageBox.Show(_("Please restart FLExTools for the changes to take effect"),
                        _("Settings changed"))


# ------------------------------------------------------------------

# To test the dialog stand-alone, run (from the FlexTools directory):
# py -m flextoolslib.code.UISettings

if __name__ == "__main__":
    Settings()
