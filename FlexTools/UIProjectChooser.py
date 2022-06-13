#
#   Project: FlexTools
#   Module:  UIProjectChooser
#   Platform: .NET v2 Windows.Forms (Python.NET 2.5)
#
#   Dialog for selecting a Fieldworks project.
#
#
#   Copyright Craig Farrow, 2010 - 2018
#

import UIGlobal
from flexlibs import FLExInitialize, FLExCleanup
from flexlibs import AllProjectNames

from System.Drawing import (Color, SystemColors, Point, Rectangle, Size, Bitmap,
                            Image, Icon,
                            Font, FontStyle, FontFamily)
from System.Windows.Forms import (Application, BorderStyle, Button,
    Form, FormBorderStyle, Label,
    Panel, Screen, FixedPanel, Padding,
    KeyEventArgs, KeyPressEventArgs, Keys,
    MessageBox, MessageBoxButtons, DialogResult,
    DockStyle, Orientation, View, SortOrder,
    ListView, ListViewItem, ColumnHeaderStyle,
    HorizontalAlignment, ImageList,
    RichTextBox, HtmlDocument, SplitContainer )


from System import ArgumentOutOfRangeException


# ------------------------------------------------------------------

class ProjectList(ListView):
    def __init__(self, currentProject):
        ListView.__init__(self)
        self.Dock = DockStyle.Fill

        # appearance
        self.BackColor = UIGlobal.rightPanelColor
        self.Font = UIGlobal.normalFont

        self.View = View.Details
        self.FullRowSelect = True
        self.HeaderStyle = getattr(ColumnHeaderStyle, "None")
        self.Columns.Add("", -2, HorizontalAlignment.Left);

        # behaviour
        self.LabelEdit = False
        self.MultiSelect = False

        # initialise the list
        self.itemToSetAsSelected = None

        for name in AllProjectNames():
            item = self.Items.Add(name)
            if name == currentProject:
                self.itemToSetAsSelected = item

    def SetActivatedHandler(self, handler):
        # Activation on Enter and Double-click
        if handler:
            self.__ActivatedHandler = handler
            self.DoubleClick += self.__ItemActivatedHandler
            self.KeyDown += self.__ItemActivatedHandler

    def __ItemActivatedHandler(self, sender, event):
        #print "__ItemActivatedHandler()"
        if self.__ActivatedHandler:
            activate = True         # For DoubleClick
            if type(event) == KeyEventArgs:
                activate = (event.KeyCode == Keys.Return)
            if activate:
                #print "SelectedItems:", sender.SelectedItems, sender.SelectedItems.Count
                try:
                    self.__ActivatedHandler(sender.SelectedItems[0].Text)
                except ArgumentOutOfRangeException:
                    #print("UIProjectChooser.__ItemActivatedHandler: ArgumentOutOfRangeException!")
                    pass # No item selected

    def SetFocusOnCurrent(self):
        ## Setting the focus during initialisation doesn't work
        ## - it needs to be set during the Form Load handler.
        if self.itemToSetAsSelected:
            self.itemToSetAsSelected.Focused = True
            self.itemToSetAsSelected.Selected = True
            self.itemToSetAsSelected.EnsureVisible()

# ------------------------------------------------------------------

class ProjectChooser(Form):

    def __init__(self, currentProject=None):
        Form.__init__(self)

        self.ClientSize = Size(350, 250)
        self.Text = "Choose Project"
        self.Icon = Icon(UIGlobal.ApplicationIcon)

        self.projectName = currentProject

        self.projectList = ProjectList(currentProject)
        self.projectList.SetActivatedHandler(self.__OnProjectActivated)

        self.Load += self.__OnLoad

        self.Controls.Add(self.projectList)

    def __OnLoad(self, sender, event):
        self.projectList.SetFocusOnCurrent()

    def __OnProjectActivated(self, projectName):
        #print "__OnProjectActivated()"
        # make selection available to caller
        self.projectName = projectName
        self.Close()


# ------------------------------------------------------------------
if __name__ == "__main__":
    FLExInitialize()

    # Demonstration:
    dlg = ProjectChooser()
    dlg.ShowDialog()
    if dlg.projectName:
         MessageBox.Show (dlg.projectName, "Project selected")

    FLExCleanup()
