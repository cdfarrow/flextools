#
#   Project: FlexTools
#   Module:  Help
#   Platform: .NET Windows.Forms (Using python.NET 3)
#
#   About Box and Help file launcher
#
#   Craig Farrow
#   2010-2025
#

from . import UIGlobal
from .. import version
import os
import sys

from flexlibs import FWShortVersion, FWCodeDir, APIHelpFile


from .FTModules import ModuleManager

from System.Drawing import (
    Color, Image,
    )

from System.Windows.Forms import (Application, BorderStyle, Button,
    Form, FormBorderStyle, Label,
    MessageBox, MessageBoxButtons, MessageBoxIcon, DialogResult,
    DockStyle,
    HorizontalAlignment,
    RichTextBox,
    PictureBox, PictureBoxSizeMode,
    )



class AboutInfo(RichTextBox):
    def __init__(self):
        RichTextBox.__init__(self)
        self.Dock = DockStyle.Fill
        self.BackColor = UIGlobal.helpDialogColor
        self.BorderStyle = getattr(BorderStyle, "None")
        self.TabStop = False  # Hides flashing caret

        self.Clear()
        self.SelectionIndent = 8
        self.SelectionRightIndent = 8
        self.SelectionAlignment = HorizontalAlignment.Center
        self.SelectionFont  = UIGlobal.headingFont
        self.SelectionColor = Color.Black
        self.AppendText("\nFLExTools\n")

        self.SelectionColor = UIGlobal.accentColor
        self.SelectionFont  = UIGlobal.smallFont
        self.AppendText(f"({version})\n\n")     # The flextoolslib version

        self.SelectionColor = UIGlobal.accentColor
        self.SelectionFont = UIGlobal.normalFont
        self.AppendText(_("A framework for running Python scripts on a FieldWorks Language Explorer project."))
        self.AppendText("\n")

        self.SelectionAlignment = HorizontalAlignment.Left
        self.SelectionFont = UIGlobal.smallFont
        self.SelectionColor = Color.Black
        self.AppendText("\n")

        mm = ModuleManager()
        mm.LoadAll()
        self.SelectionFont = UIGlobal.normalFont
        self.AppendText(_("Modules installed: {}").format(len(mm.ListOfNames()))+"\n")
        self.SelectionFont = UIGlobal.normalFont
        self.AppendText(_("Python version: {}").format(sys.version.split()[0])+"\n")
        self.SelectionFont = UIGlobal.normalFont
        self.AppendText(_("FieldWorks version: {}").format(FWShortVersion)+"\n")
        self.AppendText("\n")

        self.SelectionFont = UIGlobal.normalFont
        self.AppendText("FLExTools: \thttps://github.com/cdfarrow/flextools/wiki\n")
        self.SelectionFont = UIGlobal.normalFont
        self.AppendText("FieldWorks: \thttps://software.sil.org/fieldworks/\n")
        self.SelectionFont = UIGlobal.normalFont
        self.AppendText("{}: \tmailto:flextoolshelp".format(_("E-mail")))
        self.SelectionFont = UIGlobal.normalFont
        self.AppendText("@gmail.com\n")

        # Make it all non-editable
        self.SelectAll()
        self.SelectionProtected = True
        self.Select(10000,10000)
        self.SendToBack()

        self.LinkClicked += self.__OnLinkClicked

    def __OnLinkClicked(self, sender, event):
        try:
            os.startfile(event.LinkText)
        except WindowsError:
            MessageBox.Show("Error opening link", "Error!",
                            MessageBoxButtons.OK,
                            MessageBoxIcon.Error)


class AboutBox (Form):
    def __init__(self):
        Form.__init__(self)
        self.ClientSize = UIGlobal.aboutBoxSize
        self.Text = _("About FLExTools")
        self.FormBorderStyle  = FormBorderStyle.Fixed3D
        self.Icon = UIGlobal.ApplicationIcon

        pb = PictureBox()
        pb.Image = Image.FromFile(UIGlobal.ApplicationIconFile)
        pb.BackColor = UIGlobal.helpDialogColor
        pb.SizeMode = PictureBoxSizeMode.CenterImage

        self.Controls.Add(pb)
        self.Controls.Add(AboutInfo())


HELP_PATH = os.path.join(os.path.dirname(__file__), r"..\docs")

GeneralHelpFile     = os.path.join(HELP_PATH, "FLExTools Help.pdf")
ProgrammingHelpFile = os.path.join(HELP_PATH, "FLExTools Programming.pdf")
APIHelpFile         = APIHelpFile


def Help(helpfile):
    try:
        os.startfile(helpfile)
    except WindowsError:
        MessageBox.Show("Couldn't open help file '%s'" % helpfile,
                        "Error",
                        MessageBoxButtons.OK,
                        MessageBoxIcon.Error)


# --- Exported functions ---

def About(sender=None, event=None):
    dlg = AboutBox()
    dlg.ShowDialog()


def GeneralHelp(sender=None, event=None):
    Help(GeneralHelpFile)

def ProgrammingHelp(sender=None, event=None):
    Help(ProgrammingHelpFile)

def APIHelp(sender=None, event=None):
    Help(APIHelpFile)

def LaunchLCMBrowser(sender=None, event=None):
    os.startfile(os.sep.join((FWCodeDir, "LCMBrowser.exe")))


# ------------------------------------------------------------------

if __name__ == "__main__":
    About()
