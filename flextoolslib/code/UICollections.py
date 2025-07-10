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
#
#   Craig Farrow
#   2009-2024
#

from . import UIGlobal
from .UIModuleBrowser import ModuleBrowser
from . import FTCollections
from . import FTModules

from System.Windows.Forms import (
    Application,
    Form,
    Panel,
    KeyEventArgs, Keys,
    MessageBox, MessageBoxButtons, MessageBoxIcon, DialogResult,
    DockStyle, Orientation, View, SortOrder,
    TreeView, TreeViewAction,
    ListView, ListViewItem,
    ColumnHeaderStyle,
    ToolTip,
    TabControl, TabPage, TabAlignment,
    SplitContainer,
    )

from System import (
    ArgumentOutOfRangeException
    )

from cdfutils.DotNet import CustomToolBar

# Set of characters prohibited from collection names
INVALID_CHARS = r':\/*?"<>|'

# ------------------------------------------------------------------
class CollectionsList(ListView):
    def __init__(self):
        ListView.__init__(self)

        self.Dock = DockStyle.Fill

        # Behaviour
        self.LabelEdit = True   # Allow renaming
        self.Sorting = SortOrder.Ascending
        self.MultiSelect = False

        # Appearance: Full-width, single column display of the list
        #   View = Details
        #   Needs a Column for it to display; -2 means auto-size
        #   HeaderStyle = ColumnHeaderStyle.None to hide the header
        self.View = View.Details
        self.Columns.Add("", -2)
        self.HeaderStyle = getattr(ColumnHeaderStyle, "None")
        
        self.FullRowSelect = True
        self.HideSelection = False    # Keep selected item grey when lost focus

        self.BackColor = UIGlobal.leftPanelColor

        tooltip = ToolTip()
        tooltip.IsBalloon = True
        tooltip.SetToolTip(self, _("Double-click a collection to select it"))

        self.__SelectedHandler = None
        self.__ActivatedHandler = None

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
                    pass    # No item selected; ignore

    def AddCollection(self, collectionName):
        item = self.Items.Add(collectionName)
        item.Name = collectionName  # Add key for using Find()
        return item

# ------------------------------------------------------------------
class CollectionsModuleList(ListView):
    def __init__(self):
        ListView.__init__(self)
        self.Dock = DockStyle.Fill
        
        # Behaviour
        self.LabelEdit = False
        self.Sorting = getattr(SortOrder, "None")
        self.MultiSelect = False

        # Appearance: Full-width, single column display of the list
        #   View = Details
        #   Needs a Column for it to display; -2 means auto-size
        #   HeaderStyle = ColumnHeaderStyle.None to hide the header
        self.View = View.Details
        self.Columns.Add("", -2)
        self.HeaderStyle = getattr(ColumnHeaderStyle, "None")
        
        self.FullRowSelect = True
        self.HideSelection = False    # Keep selected item grey when lost focus
        
        self.BackColor = UIGlobal.rightPanelColor
        
    def UpdateList(self, moduleList):
        self.Items.Clear()
        for m in moduleList:
            i = self.Items.Add(m)
            i.Name = m          # Name is required for Find()

# ------------------------------------------------------------------
class CollectionsManagerUI(Panel):

    def __InitialiseToolBar(self):

        # The Collections toolbar buttons are:
        #   New, Rename, Delete | Add Module | MoveUp, MoveDown, Remove
        #
        # [Handler,
        #  Caption,
        #  Image file name, 
        #  Tool tip]
        ButtonList = [
            [
             self.__ToolbarNewHandler,
             # NOTE: Toolbar item
             _("New"),
             "documents", 
             _("Create a new collection"),
            ],
            [
             self.__ToolbarRenameHandler,
             # NOTE: Toolbar item
             _("Rename"),
             "copy", 
             _("Rename the selected collection"),
            ],
            [
             self.__ToolbarDeleteHandler,
             # NOTE: Toolbar item
             _("Delete"),
             "trash", 
             _("Delete the selected collection"),
            ],
            [
             self.__ToolbarSelectAndCloseHandler,
             # NOTE: Toolbar item
             _("Select"),
             "folder-closed", 
             _("Close this dialog"),
            ],            
            None,   # Separator
            [
             self.__ToolbarAddHandler,
             # NOTE: Toolbar item
             _("Add Module"),
             "add", 
             _("Add a module to the current collection"),
            ],
            None,   # Separator
            [
             self.__ToolbarMoveUpHandler,
             # NOTE: Toolbar item
             _("Move Up"),
             "arrow-up", 
             _("Move the selected module up"),
            ],
            [
             self.__ToolbarMoveDownHandler,
             # NOTE: Toolbar item
             _("Move Down"),
             "arrow-down", 
             _("Move the selected module down"),
            ],
            [
             self.__ToolbarRemoveHandler,
             # NOTE: Toolbar item
             _("Remove"),
             "delete", 
             _("Remove the selected module from the current collection"),
            ],
            ]
            
        return CustomToolBar(ButtonList, 
                             UIGlobal.ToolbarIconParams)

    # The toolbar buttons are enabled/disabled according to where the
    # UI focus is. These values are indices into the ButtonList parameters.
    INFOCUS_Nothing = -1
    INFOCUS_Collections = 0
    INFOCUS_ModuleLibrary = 1
    INFOCUS_CollectionModules = 2

    ButtonEnableStates = [
       # InCollections, InModules, InModuleLibrary,
       [True, False, False],    # New
       [True, False, False],    # Rename
       [True, False, False],    # Delete
       [True, False, False],    # Close
       None,
       [False, True, False],    # Add
       None,
       [False, False, True],    # Up
       [False, False, True],    # Down
       [False, False, True],    # Remove
       ]

    def __SetEnabledStates(self, inFocus):
        for i, button in enumerate(self.toolbar.Items):
            if inFocus == self.INFOCUS_Nothing:
                button.Enabled = False
            else:
                if self.ButtonEnableStates[i]:   # Skip separators
                    button.Enabled = self.ButtonEnableStates[i][inFocus]

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
        self.toolbar = self.__InitialiseToolBar()
        self.toolbar.Font = UIGlobal.normalFont

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
        self.collectionsTabPage.Text = _("Collections")
        self.collectionsTabControl = TabControl()
        self.collectionsTabControl.Dock = DockStyle.Fill
        self.collectionsTabControl.Alignment = TabAlignment.Left
        self.collectionsTabControl.TabStop = False
        self.collectionsTabControl.TabPages.Add(self.collectionsTabPage)

        self.modulesTabPage = TabPage()
        self.modulesTabPage.Controls.Add(self.moduleBrowser)
        self.modulesTabPage.Text = _("Modules")
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

        # Add the main SplitContainer control to the panel.
        self.Controls.Add(self.splitContainer2)
        self.Controls.Add(self.toolbar)     # Last in takes space priority

    # -- Exported methods

    def SetFocusOnCurrentCollection(self):
        # Setting the focus during initialisation doesn't work
        # - it needs to be set during the Form Load handler.
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
                MessageBox.Show(_("This module is already in the current collection."),
                                _("Duplicate module"),
                                MessageBoxButtons.OK,
                                MessageBoxIcon.Information)
            else:
                self.modulesList.Items.Add(moduleName)
                self.modulesList.EnsureVisible(self.modulesList.Items.Count-1) 

    def __OnCollectionSelected(self, collectionName):
        self.currentCollection = collectionName
        self.modulesList.UpdateList(self.collections.ListOfModules(collectionName))

    def __OnCollectionRenamed(self, sender, event):
        # Determine if the label has been changed by checking for null.
        if not event.Label:
            return
        # Don't bother if the user didn't actually change the name.
        if self.currentCollection != event.Label:
            errorMsg = None
            # Guard against invalid file/path characters in the name.
            if set(INVALID_CHARS).intersection(event.Label):
                errorMsg = _("A collection name cannot include any of these symbols: {}").format(" ".join(INVALID_CHARS))
            else:
                try:
                    self.collections.Rename(self.currentCollection, event.Label)
                except (FTCollections.FTC_NameError,
                        FTCollections.FTC_ExistsError,
                        FTCollections.FTC_BadNameError) as e:
                    errorMsg = e.message
                    
            if not errorMsg:
                self.currentCollection = event.Label
                # Update the Name for Find() to work
                self.collectionsList.Items[event.Item].Name = event.Label 
            else:
                # Cancel the event and return the label to its original state.
                event.CancelEdit = True
                MessageBox.Show(errorMsg, 
                                _("Renaming error"),
                                MessageBoxButtons.OK,
                                MessageBoxIcon.Error)
        return

    # -- Toolbar button handlers
    
    def __ToolbarNewHandler(self, sender=None, event=None):
        name = _("New collection")
        # If this name still exists, then just go to that and rename it.
        if name in self.collections.Names():
            try:
                item = self.collectionsList.Items.Find(name, False)[0]
            except ArgumentOutOfRangeException:
                return      # This is an error if the item can't be found.
        else:
            self.collections.Add(name)
            item = self.collectionsList.AddCollection(name)
        item.BeginEdit()

    def __ToolbarDeleteHandler(self, sender=None, event=None):
        try:
            itemToDelete = self.collectionsList.SelectedItems[0]
        except ArgumentOutOfRangeException:
            return          # There is nothing selected
            
        moduleName = itemToDelete.Text
        message = _("Are you sure you want to delete the collection '{}'?")
        title = _("Confirm delete")
        result = MessageBox.Show(message.format(moduleName), 
                                 title,
                                 MessageBoxButtons.YesNo,
                                 MessageBoxIcon.Question)

        if result == DialogResult.Yes:
            self.collections.Delete(moduleName)
            itemToDelete.Remove()
            # No collection is selected at this point, so just
            # clear the modules List.
            self.currentCollection = None
            self.modulesList.Items.Clear()

    def __ToolbarRenameHandler(self, sender=None, event=None):
        try:
            item = self.collectionsList.SelectedItems[0]
        except ArgumentOutOfRangeException:
            return          # There is nothing selected

        item.BeginEdit()
            
    def __ToolbarAddHandler(self, sender=None, event=None):
        if self.moduleBrowser.selectedNode:
            self.__OnModuleActivated(self.moduleBrowser.selectedNode)

    def ___MoveItemInList(self, item, newIndex):
        self.modulesList.BeginUpdate()
        self.modulesList.Items.Remove(item)
        self.modulesList.Items.Insert(newIndex, item)
        self.modulesList.FocusedItem = item
        self.modulesList.EnsureVisible(newIndex) 
        self.modulesList.EndUpdate()

    def __ToolbarMoveUpHandler(self, sender=None, event=None):
        try:
            itemToMove = self.modulesList.SelectedItems[0]
        except ArgumentOutOfRangeException:
            return          # There is nothing selected
            
        if itemToMove.Index < 1:
            return
        
        newIndex = itemToMove.Index - 1

        self.___MoveItemInList(itemToMove, newIndex)
        self.collections.MoveModuleUp(self.currentCollection,
                                      itemToMove.Text)

    def __ToolbarMoveDownHandler(self, sender=None, event=None):
        try:
            itemToMove = self.modulesList.SelectedItems[0]
        except ArgumentOutOfRangeException:
            return          # There is nothing selected
            
        if itemToMove.Index >= self.modulesList.Items.Count - 1:
            return
        
        newIndex = itemToMove.Index + 1
                
        self.___MoveItemInList(itemToMove, newIndex)
        self.collections.MoveModuleDown(self.currentCollection,
                                        itemToMove.Text)
                        
    def __ToolbarRemoveHandler(self, sender=None, event=None):
        try:
            itemToRemove = self.modulesList.SelectedItems[0]
        except ArgumentOutOfRangeException:
            return          # There is nothing selected
        
        self.collections.RemoveModule(self.currentCollection,
                                      itemToRemove.Text)
        itemToRemove.Remove()

    def __ToolbarSelectAndCloseHandler(self, sender=None, event=None):
        self.Parent.Close()

    def __ChangeOfFocusHandler(self, sender, event):
        if self.collectionsList.Focused:
            focus = self.INFOCUS_Collections
        elif self.modulesList.Focused:
            focus = self.INFOCUS_CollectionModules
        elif self.moduleBrowser.ContainsFocus:
            focus = self.INFOCUS_ModuleLibrary
        else:
            focus = self.INFOCUS_Nothing
        self.__SetEnabledStates(focus)

# ------------------------------------------------------------------
class CollectionsDialog(Form):
    def __init__(self, cm, mm, currentCollection):
        Form.__init__(self)
        self.ClientSize = UIGlobal.collectionsWindowSize
        self.Text = _("Collections Manager")
        self.Icon = UIGlobal.ApplicationIcon

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
    form.ClientSize = UIGlobal.collectionsWindowSize
    form.Text = "Test of Collections Manager"

    form.Controls.Add(cmPanel)
    Application.Run(form)
