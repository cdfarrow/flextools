#
#   Project: FlexTools
#   Module:  Help
#   Platform: .NET v2 Windows.Forms (Python.NET 2.5)
#
#   About Box and Help file launcher
#
#   Craig Farrow
#   Nov 2010
#

import UIGlobal
import Version
import os
import sys

from flexlibs import FWShortVersion, FWCodeDir, APIHelpFile


from FTModules import ModuleManager

from System.Drawing import (Color, SystemColors, Point, PointF, Rectangle,
                            Size, Bitmap, Image, Icon,
                            SolidBrush, Pens, Font, FontStyle, FontFamily)

from System.Windows.Forms import (Application, BorderStyle, Button,
    Form, FormBorderStyle, Label,
    MessageBox, MessageBoxButtons, MessageBoxIcon, DialogResult,
    DockStyle, Orientation, View, SortOrder,
    HorizontalAlignment, ImageList,
    RichTextBox, RichTextBoxScrollBars, ControlStyles,
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

        self.SelectionColor = Color.DarkSlateBlue
        self.SelectionFont  = UIGlobal.smallFont
        self.AppendText("%s\n\n" % Version.number)

        self.SelectionColor = Color.DarkSlateBlue
        self.SelectionFont = UIGlobal.normalFont
        self.AppendText("A framework for running Python scripts on a Fieldworks Language Explorer database. \n")

        self.SelectionAlignment = HorizontalAlignment.Left
        self.SelectionFont = UIGlobal.smallFont
        self.SelectionColor = Color.Black
        self.AppendText("\n")

        mm = ModuleManager()
        mm.LoadAll()
        self.SelectionFont = UIGlobal.normalFont
        self.AppendText("Modules installed: %d\n" % len(mm.ListOfNames()))
        self.SelectionFont = UIGlobal.normalFont
        self.AppendText("Python version: %s\n" % sys.version.split()[0])
        self.SelectionFont = UIGlobal.normalFont
        self.AppendText("Fieldworks version: %s\n\n" %
                            FWShortVersion)

        self.SelectionFont = UIGlobal.normalFont
        self.AppendText("FLExTools: \thttps://github.com/cdfarrow/flextools/wiki\n")
        self.SelectionFont = UIGlobal.normalFont
        self.AppendText("Fieldworks: \thttps://software.sil.org/fieldworks/\n")
        self.SelectionFont = UIGlobal.normalFont
        self.AppendText("E-mail: \tmailto:flextoolshelp")
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
        self.ClientSize = Size(400, 250)
        self.Text = "About FLExTools"
        self.FormBorderStyle  = FormBorderStyle .Fixed3D
        self.Icon = Icon(UIGlobal.ApplicationIcon)

        pb = PictureBox()
        pb.Image = Image.FromFile(UIGlobal.ApplicationIcon)
        pb.BackColor = UIGlobal.helpDialogColor
        pb.SizeMode = PictureBoxSizeMode.CenterImage

        self.Controls.Add(pb)
        self.Controls.Add(AboutInfo())


HELP_PATH = os.path.join(os.path.dirname(__file__), "..\docs")

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
