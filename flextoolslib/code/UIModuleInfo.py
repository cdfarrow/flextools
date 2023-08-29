#
#   Project: FlexTools
#   Module:  UIModuleInfo
#   Platform: .NET v2 Windows.Forms
#
#   UI for the module information for use in the Collections Manager
#   and the Module Info dialog from the main list.
#
#   Craig Farrow
#   Oct 2009
#

import os

from . import UIGlobal
from .FTModuleClass import *

from System.Drawing import (Color, Point, Rectangle, Size, Bitmap,
                            Icon,
                            Font, FontStyle, FontFamily)
from System.Windows.Forms import (Application, BorderStyle, Button,
    Form, FormBorderStyle,
    MessageBox, MessageBoxButtons, MessageBoxIcon, 
    RichTextBox, 
    DockStyle,
    HorizontalAlignment,
    ToolTip,
    )

# ------------------------------------------------------------------

class ModuleInfoPane(RichTextBox):
    def __init__(self):
        RichTextBox.__init__(self)
        self.Dock = DockStyle.Fill
        self.BackColor = UIGlobal.rightPanelColor
        self.SelectionProtected = True
        self.TabIndex = 1
        self.LinkClicked += self.__OnLinkClicked

    def SetFromDocs(self, moduleDocs):
        self.Clear()

        # Module Name
        self.SelectionFont = UIGlobal.headingFont
        self.SelectionAlignment = HorizontalAlignment.Center
        self.AppendText(moduleDocs[FTM_Name]+"\n")

        self.SelectionIndent = 8

        self.SelectionAlignment = HorizontalAlignment.Left

        # Module Version
        self.SelectionFont = UIGlobal.normalFont
        self.SelectionColor = Color.Blue
        self.AppendText("\nVersion: %s\n" % str(moduleDocs[FTM_Version]))

        # Modification warning
        if moduleDocs[FTM_ModifiesDB]:
             self.SelectionFont = UIGlobal.normalFont
             self.SelectionColor = Color.Red
             self.AppendText("Can modify the project\n")

        # Module Synopsis
        self.SelectionColor = Color.DarkSlateBlue
        self.SelectionFont = UIGlobal.normalFont
        self.AppendText(moduleDocs[FTM_Synopsis]+"\n")

        # Module Help
        if FTM_Help in moduleDocs and moduleDocs[FTM_Help]:
            self.SelectionFont = UIGlobal.normalFont
            self.AppendText("Help: ")
            
            link = "file:%s\n" % moduleDocs[FTM_Help]
            # Change spaces to underscores so the whole path is treated as a hyperlink
            self.AppendText(link.replace(" ", "_"))
            # Build the actual hyperlink with full path
            self.HelpLink = os.path.sep.join((os.path.split(moduleDocs[FTM_Path])[0],
                                              moduleDocs[FTM_Help]))

        self.SelectionFont = UIGlobal.smallFont
        self.AppendText("\n")        

        # Module Description
        self.SelectionColor = Color.Black

        start = self.SelectionStart
        # convert all single newlines to spaces
        md = moduleDocs[FTM_Description].replace("\n\n", "<break>").split()
        md = " ".join(md).replace("<break>", "\n\n")
        self.AppendText(md)
        
        # Chinese text messes up the font: setting the font after Append fixes it. 
        self.Select(start,self.TextLength)      # Start, Length
        self.SelectionFont = UIGlobal.normalFont
        self.AppendText("\n")                  # NL, and puts insertion point at end.

        # Module filename
        self.SelectionIndent = 0
        self.SelectionHangingIndent = 0
        self.SelectionRightIndent = 0
        self.SelectionColor = Color.Black
        self.SelectionFont = UIGlobal.smallFont
        self.AppendText("\nSource file: " + moduleDocs[FTM_Path] + ".py\n")

        # Make it non-editable
        self.SelectAll()
        self.SelectionProtected = True
        self.Select(0,0)

    def __OnLinkClicked(self, sender, event):
        try:
            os.startfile(self.HelpLink)
        except WindowsError as e:
            MessageBox.Show("Error opening link: %s" % self.HelpLink,
                            "Error!" ,
                            MessageBoxButtons.OK,
                            MessageBoxIcon.Error)

# ------------------------------------------------------------------

class ModuleInfoDialog(Form):
    def __init__(self, docs):
        Form.__init__(self)
        self.ClientSize = Size(400, 400)
        self.Text = "Module Details"
        self.Icon = Icon(UIGlobal.ApplicationIcon)

        infoPane = ModuleInfoPane()
        infoPane.SetFromDocs(docs)
        self.Controls.Add(infoPane)
