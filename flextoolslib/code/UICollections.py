#
#   Project: FlexTools
#   Module:  UICollections
#   Platform: .NET v2 Windows.Forms
#
#   UI for browsing, creating and editing collections of modules:
#   A split container:
#       - The top half shows the collections:
#           - A list of collections on the left
#           - A list of modules in the selected collection on the right.
#       - The bottom half is the list of installed modules, with an
#         information panel to the right (UI supplied by UIModuleBrowser)
#
#   TODO:
#    -  4 Nov 09: Get the collection list to sort after renaming an item
#    -  5 Nov 09: Highlight the whole row in both lists
#
#   Craig Farrow
#   Oct 2009
#

import UIGlobal
from UIModuleBrowser import ModuleBrowser
import FTCollections
import FTModules


from System.Drawing import (Color, SystemColors, Point, Rectangle, Size, Bitmap,
                            Image, Icon,
                            Font, FontStyle, FontFamily)
from System.Windows.Forms import (Application, BorderStyle, Button,
    Form, FormBorderStyle, Label,
    Panel, Screen, FixedPanel, Padding,
    KeyEventArgs, KeyPressEventArgs, Keys,
    MessageBox, MessageBoxButtons, MessageBoxIcon, DialogResult,
    DockStyle, Orientation, View, SortOrder,
    TreeView, TreeViewAction,
    ListView, ListViewItem,
    ToolTip,
    TabControl, TabPage, TabAlignment,
    ToolBar, ToolBarButton, ToolBarButtonStyle, ToolBarAppearance,
    HorizontalAlignment, ImageList,
    RichTextBox, HtmlDocument, SplitContainer )

from System import (
    ArgumentOutOfRangeException
    )


# ------------------------------------------------------------------
class CollectionsToolbar(ToolBar):
    """
Toolbar has New, Rename, Delete | MoveUp, MoveDown | Add Module
    """

    # The toolbar buttons are enabled/disabled according to where the
    # UI focus is. These values are indices into the ButtonList parameters.
    INFOCUS_Nothing = 0
    INFOCUS_Collections = 1
    INFOCUS_ModuleLibrary = 2
    INFOCUS_CollectionModules = 3
    __BUTTON_Text = 0
    __BUTTON_Image = 4
    __BUTTON_Tooltip = 5

    # [Text,
    #  EnabledInCollections, EnabledInModules, EnabledInModuleLibrary,
    #  Image name, Tool tip]
    ButtonList = [["New",
                   True, False, False,
                   "documents", "Create a new module collection"],
                  ["Rename",
                   True, False, False,
                   "copy", "Rename the selected collection"],
                  ["Delete",
                   True, False, False,
                   "delete", "Delete the selected collection"],
                  None, # Separator
                  ["Add Module",
                   False, True, False,
                   "add", "Add a module to the current module collection"],
                  None, # Separator
                  ["Move Up",
                   False, False, True,
                   "arrow-up", "Move the selected module up"],
                  ["Move Down",
                   False, False, True,
                   "arrow-down", "Move the selected module down"],
                  ["Remove",
                   False, False, True,
                   "delete", "Remove the selected module"],
                   ]

    def __init__(self):
        ToolBar.__init__(self)
        self.Appearance = ToolBarAppearance.Flat
        self.Dock = DockStyle.Top

        self.ImageList = ImageList()

        for b in self.ButtonList:
            self.__buttonBuilder(b)

    def __buttonBuilder(self, buttonDetails):
        button = ToolBarButton()
        if buttonDetails:
            button.Text = buttonDetails[self.__BUTTON_Text]
            button.ToolTipText = buttonDetails[self.__BUTTON_Tooltip]
            self.ImageList.Images.Add(
                Bitmap.FromFile(buttonDetails[self.__BUTTON_Image].join(
                                    UIGlobal.ToolbarIconParams)))
            button.ImageIndex = self.ImageList.Images.Count-1
            button.Tag = buttonDetails
        else:
            button.Style = ToolBarButtonStyle.Separator
        self.Buttons.Add(button)

    def SetEnabledStates(self, inFocus):
        if inFocus == self.INFOCUS_Nothing:
            for b in self.Buttons:
                if b.Tag:
                    b.Enabled = False
        else:
            for b in self.Buttons:
                if b.Tag:
                    b.Enabled = b.Tag[inFocus] # Values 1,2,3


# ------------------------------------------------------------------

class CollectionsList(ListView):
    def __init__(self):
        ListView.__init__(self)

        self.Dock = DockStyle.Fill

        # behaviour
        self.LabelEdit = True # allow renaming
        self.Sorting = SortOrder.Ascending
        self.MultiSelect = False

        # appearance
        self.View = View.SmallIcon
        self.ShowLines = True
        self.TabIndex = 0
        self.BackColor = UIGlobal.leftPanelColor
        self.HideSelection = False    # Keep selected item grey when lost focus

        tooltip = ToolTip()
        tooltip.IsBalloon = True
        tooltip.SetToolTip(self, "Double-click a collection to select it.")


    def SetSelectedHandler(self, handler):
        self.__SelectedHandler = handler
        self.ItemSelectionChanged += self.__ItemSelectedHandler

    def __ItemSelectedHandler(self, sender, event):
        if event.IsSelected:
            if self.__SelectedHandler:
                self.__SelectedHandler(event.Item.Text)


    def SetActivatedHandler(self, handler):
        if handler:
            self.__ActivatedHandler = handler
            self.DoubleClick += self.__ItemActivatedHandler
            self.KeyDown += self.__ItemActivatedHandler

    def __ItemActivatedHandler(self, sender, event):
        if self.__ActivatedHandler:
            activate = True         # For DoubleClick
            if type(event) == KeyEventArgs:
                activate = (event.KeyCode == Keys.Return)
            if activate:
                try:
                    self.__ActivatedHandler(sender.SelectedItems[0].Text)
                except ArgumentOutOfRangeException:
                    pass # No item selected; ignore

    def AddCollection(self, collectionName):
        item = self.Items.Add(collectionName)
        item.Name = collectionName  # Add key for using Find()
        return item



# ------------------------------------------------------------------

class CollectionsModuleList(ListView):
    def __init__(self):
        ListView.__init__(self)
        self.Dock = DockStyle.Fill
        self.BackColor = UIGlobal.rightPanelColor
        self.LabelEdit = False
        self.Sorting = getattr(SortOrder, "None")
        self.View = View.List
        self.MultiSelect = False

    def UpdateList(self, moduleList):
        self.Clear()
        for m in moduleList:
            i = self.Items.Add(m)
            i.Name = m          # Name is required for Find()

# ------------------------------------------------------------------

class CollectionsManagerUI(Panel):
    def __init__(self, collectionsManager, moduleManager, currentCollection):
        Panel.__init__(self)
        self.collections = collectionsManager

        self.Dock = DockStyle.Fill
        self.Font = UIGlobal.normalFont

        # -- Collections and module lists
        self.collectionsList = CollectionsList()
        self.modulesList = CollectionsModuleList()
        self.currentCollection = currentCollection

        # -- Load the collections list
        self.itemToSetAsSelected = None
        for c in self.collections.Names():
            item = self.collectionsList.AddCollection(c)
            if c == currentCollection:
                self.itemToSetAsSelected = item

        # -- Handlers
        self.collectionsList.SetSelectedHandler(self.__OnCollectionSelected)
        self.collectionsList.AfterLabelEdit += self.__OnCollectionRenamed

        # -- Modules list and info
        self.moduleBrowser = ModuleBrowser(moduleManager)
        self.moduleBrowser.SetActivatedHandler(self.__OnModuleActivated)

        # -- Toolbar
        self.toolbar = CollectionsToolbar()
        self.toolbar.ButtonClick += self.__ToolbarButtonHandler

        self.collectionsList.GotFocus += self.__ChangeOfFocusHandler
        self.collectionsList.LostFocus += self.__ChangeOfFocusHandler
        self.modulesList.GotFocus += self.__ChangeOfFocusHandler
        self.modulesList.LostFocus += self.__ChangeOfFocusHandler
        self.moduleBrowser.moduleTree.GotFocus += self.__ChangeOfFocusHandler
        self.moduleBrowser.moduleTree.LostFocus += self.__ChangeOfFocusHandler

        # -- Put it all together
        self.splitContainer1 = SplitContainer()
        self.splitContainer1.Dock = DockStyle.Fill
        self.splitContainer1.TabIndex = 1
        self.splitContainer1.SplitterWidth = UIGlobal.SPLITTER_WIDTH
        self.splitContainer1.SplitterDistance = 50
        self.splitContainer1.Orientation = Orientation.Vertical
        self.splitContainer1.Panel1.Controls.Add(self.collectionsList)
        self.splitContainer1.Panel2.Controls.Add(self.modulesList)

        self.collectionsTabPage = TabPage()
        self.collectionsTabPage.Controls.Add(self.splitContainer1)
        self.collectionsTabPage.Text = "Collections"
        self.collectionsTabControl = TabControl()
        self.collectionsTabControl.Dock = DockStyle.Fill
        self.collectionsTabControl.Alignment = TabAlignment.Left
        self.collectionsTabControl.TabStop = False
        self.collectionsTabControl.TabPages.Add(self.collectionsTabPage)

        self.modulesTabPage = TabPage()
        self.modulesTabPage.Controls.Add(self.moduleBrowser)
        self.modulesTabPage.Text = "Modules"
        self.modulesTabControl = TabControl()
        self.modulesTabControl.Dock = DockStyle.Fill
        self.modulesTabControl.Alignment = TabAlignment.Left
        self.modulesTabControl.TabStop = False
        self.modulesTabControl.TabPages.Add(self.modulesTabPage)

        self.splitContainer2 = SplitContainer()
        self.splitContainer2.Dock = DockStyle.Fill
        self.splitContainer2.TabIndex = 2
        self.splitContainer2.SplitterWidth = UIGlobal.SPLITTER_WIDTH
        self.splitContainer2.SplitterDistance = 30
        self.splitContainer2.Orientation = Orientation.Horizontal
        self.splitContainer2.Panel1.Controls.Add(self.collectionsTabControl)
        self.splitContainer2.Panel2.Controls.Add(self.modulesTabControl)

        ## Add the main SplitContainer control to the panel.
        self.Controls.Add(self.splitContainer2)
        self.Controls.Add(self.toolbar) # Last in takes space priority

    # -- Exported methods

    def SetFocusOnCurrentCollection(self):
        ## Setting the focus during initialisation doesn't work
        ## - it needs to be set during the Form Load handler.
        if self.itemToSetAsSelected:
            self.itemToSetAsSelected.Focused = True
            self.itemToSetAsSelected.Selected = True
            self.itemToSetAsSelected.EnsureVisible()

    def SaveAll(self):
        self.collections.WriteAll()

    def SetActivatedHandler(self, activatedHandler):
        self.collectionsList.SetActivatedHandler(activatedHandler)

    # -- Private handlers

    def __OnModuleActivated(self, moduleName):
        if self.currentCollection:
            try:
                self.collections.AddModule(self.currentCollection,
                                           moduleName)
            except FTCollections.FTC_ExistsError:
                MessageBox.Show("This module is already in the current collection",
                                "Duplicate Module",
                                MessageBoxButtons.OK,
                                MessageBoxIcon.Information)
            else:
                self.modulesList.Items.Add(moduleName)

    def __OnCollectionSelected(self, itemName):
        self.currentCollection = itemName
        self.modulesList.UpdateList(self.collections.ListOfModules(itemName))

    def __OnCollectionRenamed(self, sender, event):
        # Determine if label is changed by checking for null.
        if not event.Label:
            return
        # Don't bother if user didn't acutally change the name.
        if self.currentCollection != event.Label:
            try:
                self.collections.Rename(self.currentCollection, event.Label)
            except (FTCollections.FTC_NameError,
                    FTCollections.FTC_ExistsError,
                    FTCollections.FTC_BadNameError) as e:
                # Cancel the event and return the label to its original state.
                event.CancelEdit = True
                MessageBox.Show (e.message, "Renaming error",
                                 MessageBoxButtons.OK,
                                 MessageBoxIcon.Error)
            else:
                self.currentCollection = event.Label
                event.Name = event.Label # Update for Find() function
        return


    def __ToolbarButtonHandler(self, sender, event):
        if event.Button.Text == "New":
            name = "New collection"
            # If this name still exists, then just go to that and rename it.
            if name in self.collections.Names():
                items = self.collectionsList.Items.Find(name, False)
                if len(items) > 0:
                    c = items[0]
                #print("Find returned:", c)
            else:
                self.collections.Add(name)
                c = self.collectionsList.AddCollection(name)
            c.BeginEdit()

        elif event.Button.Text == "Delete":
            selection = self.collectionsList.SelectedItems
            if selection.Count > 0:
                message = "Are you sure you want to delete collection '" +\
                          selection[0].Text +"'?"
                caption = "Confirm delete"
                result = MessageBox.Show(message, caption,
                                         MessageBoxButtons.YesNo,
                                         MessageBoxIcon.Question)

                if result == DialogResult.Yes:
                    self.collections.Delete(selection[0].Text)
                    selection[0].Remove()
                    # No collection is selected at this point, so just
                    # clear the modules List.
                    self.currentCollection = None
                    self.modulesList.Clear()

        elif event.Button.Text == "Rename":
            selection = self.collectionsList.SelectedItems
            if selection.Count > 0:
                selection[0].BeginEdit()

        elif event.Button.Text == "Move Up":
            selection = self.modulesList.SelectedItems
            if selection.Count > 0:
                moduleName = selection[0].Text
                self.collections.MoveModuleUp(self.currentCollection,
                                              moduleName)
                # Re-create the list and select the same item
                self.__OnCollectionSelected(self.currentCollection)
                items = self.modulesList.Items.Find(moduleName, False)
                if len(items) > 0:
                    items[0].Selected = True

        elif event.Button.Text == "Move Down":
            selection = self.modulesList.SelectedItems
            if selection.Count > 0:
                moduleName = selection[0].Text
                self.collections.MoveModuleDown(self.currentCollection,
                                                moduleName)
                # Re-create the list and select the same item
                self.__OnCollectionSelected(self.currentCollection)
                items = self.modulesList.Items.Find(moduleName, False)
                if len(items) > 0:
                    items[0].Selected = True

        elif event.Button.Text == "Remove":
            selection = self.modulesList.SelectedItems
            if selection.Count > 0:
                self.collections.RemoveModule(self.currentCollection,
                                              selection[0].Text)
                selection[0].Remove()

        elif event.Button.Text == "Add Module":
            if self.moduleBrowser.selectedNode:
                self.__OnModuleActivated(self.moduleBrowser.selectedNode)



    def __ChangeOfFocusHandler(self, sender, event):
        if self.collectionsList.Focused:
            focus = self.toolbar.INFOCUS_Collections
        elif self.modulesList.Focused:
            focus = self.toolbar.INFOCUS_CollectionModules
        elif self.moduleBrowser.ContainsFocus:
            focus = self.toolbar.INFOCUS_ModuleLibrary
        else:
            focus = self.toolbar.INFOCUS_Nothing
        self.toolbar.SetEnabledStates(focus)

# ------------------------------------------------------------------

class CollectionsDialog(Form):
    def __init__(self, cm, mm, currentCollection):
        Form.__init__(self)
        self.ClientSize = Size(600, 600)
        self.Text = "Collections Manager"
        self.Icon = Icon(UIGlobal.ApplicationIcon)


        self.activatedCollection = None

        self.cmPanel = CollectionsManagerUI(cm, mm, currentCollection)
        self.cmPanel.SetActivatedHandler(self.__OnCollectionActivated)

        self.Load += self.__OnLoad

        self.Controls.Add(self.cmPanel)
        self.FormClosing += self.__OnFormClosing


    def __OnLoad(self, sender, event):
        self.cmPanel.SetFocusOnCurrentCollection()

    def __OnCollectionActivated(self, collectionName):
        # make selection available to caller
        self.activatedCollection = collectionName
        self.Close()

    def __OnFormClosing(self, sender, event):
        self.activatedCollection = self.cmPanel.currentCollection
        self.cmPanel.SaveAll()


# ------------------------------------------------------------------
if __name__ == "__main__":
    collections = FTCollections.CollectionsManager()
    mm = FTModules.ModuleManager()
    mm.LoadAll()

    cmPanel = CollectionsManagerUI(collections, mm, None)

    form = Form()
    form.ClientSize = Size(600, 550)
    form.Text = "Test of Collections Manager"

    form.Controls.Add(cmPanel)
    Application.Run(form)
