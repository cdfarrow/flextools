#
#   Project: FlexTools
#   Module:  UIDbChooser
#   Platform: .NET v2 Windows.Forms
#
#   Dialog for selecting a Fieldworks database.
#   
#
#   TODO:
#
#   Craig Farrow
#   Nov 2010
#   v0.0.0
#



import UIGlobal
import FLExDBAccess


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

class DatabaseList(ListView):
    def __init__(self, currentDatabase):
        ListView.__init__(self)
        self.Dock = DockStyle.Fill

        # appearance
        self.BackColor = UIGlobal.rightPanelColor
        self.Font = UIGlobal.normalFont

        self.View = View.Details
        self.FullRowSelect = True
        self.HeaderStyle = ColumnHeaderStyle.None
        self.Columns.Add("", -2, HorizontalAlignment.Left);

        # behaviour
        self.LabelEdit = False
        self.MultiSelect = False

        # initialise the list
        self.itemToSetAsSelected = None

        self.flexDB = FLExDBAccess.FLExDBAccess()
        for name in self.flexDB.GetDatabaseNames():
            item = self.Items.Add(name)
            if name == currentDatabase:
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
                    print "ArgumentOutOfRangeException!"
                    pass # No item selected

    def SetFocusOnCurrent(self):
        ## Setting the focus during initialisation doesn't work
        ## - it needs to be set during the Form Load handler.
        if self.itemToSetAsSelected:
            self.itemToSetAsSelected.Focused = True
            self.itemToSetAsSelected.Selected = True
            self.itemToSetAsSelected.EnsureVisible()
            
# ------------------------------------------------------------------

class DatabaseChooser(Form):
    
    def __init__(self, currentDatabase=None):
        Form.__init__(self)
        
        self.ClientSize = Size(300, 250)
        self.Text = "Choose Database"
        self.Icon = Icon(UIGlobal.ApplicationIcon)

        self.databaseName = currentDatabase
        
        self.databaseList = DatabaseList(currentDatabase)
        self.databaseList.SetActivatedHandler(self.__OnDatabaseActivated)
        
        self.Load += self.__OnLoad
        
        self.Controls.Add(self.databaseList)

    def __OnLoad(self, sender, event):
        self.databaseList.SetFocusOnCurrent()

    def __OnDatabaseActivated(self, databaseName):
        #print "__OnDatabaseActivated()"
        # make selection available to caller
        self.databaseName = databaseName
        self.Close()
    

# ------------------------------------------------------------------
if __name__ == "__main__":

    # Demonstration:
    dlg = DatabaseChooser()
    dlg.ShowDialog()
    if dlg.databaseName:
         MessageBox.Show (dlg.databaseName, "Database selected")
         
