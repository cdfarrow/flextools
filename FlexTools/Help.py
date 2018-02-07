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
import os, sys

import FLExFDO
from FLExBaseInit import FWAppVersion, FWCodeDir

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
        self.BorderStyle = BorderStyle.None
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
        self.AppendText("Fieldworks version: %s\n\n" % FWAppVersion)

        self.SelectionFont = UIGlobal.normalFont
        self.AppendText("Fieldworks: \thttp://fieldworks.sil.org\n")
        self.SelectionFont = UIGlobal.normalFont
        self.AppendText("FLExTools: \thttp://craigstips.wikispaces.com/flexapps\n")
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


GeneralHelpFile     = "FLExTools Help.pdf"
ProgrammingHelpFile = "FLExTools Programming.pdf"
APIHelpFile         = "FLExTools API\\index.html"

def Help(helpfile):
    try:
        os.startfile(os.sep.join(("Help", helpfile)))
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

def LaunchFDOBrowser(sender=None, event=None):
    os.startfile(os.sep.join((FWCodeDir, "FDOBrowser.exe")))

    
# ------------------------------------------------------------------
        
if __name__ == "__main__":
    About()
