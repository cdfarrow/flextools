#
#   Project: FlexTools
#   Module:  UIMain
#   Platform: .NET v2 Windows.Forms (Python.NET 2.7)
#
#   Main FlexTools UI:
#    - A split panel with Collections list above and Report results below.
#
#   Configuration:
#       If FTConfig.simplifiedRunOps is True, then the Dry-run/Preview 
#       buttons and menu items are not shown. All Run actions behave as 
#       "Run Modify".
#       (This option can't be changed dynamically at runtime.)
#       If FTConfig.warnOnModify is False, then no warning dialog is shown
#       when running with changes enabled. This is independent of 
#       simplifiedRunOps.
#       If FTConfig.disableDoubleClick is True, then double-clicking a 
#       module will not run it. (Double click is ignored.)
#       If FTConfig.stopOnError is True, then processing will stop after
#       any module that outputs an error message.
#
#   Copyright Craig Farrow, 2010 - 2024
#


import logging
logger = logging.getLogger(__name__)


import clr
import System

clr.AddReference("System.Drawing")
from System.Drawing import (Color, SystemColors, Point, PointF, Rectangle,
                            Size, Bitmap, Image, Icon,
                            SolidBrush, Pens, Font, FontStyle, FontFamily)

clr.AddReference("System.Windows.Forms")
from System.Windows.Forms import (
    Application, 
    BorderStyle, Button,
    Form, FormBorderStyle, Label,
    Panel, Screen, FixedPanel, Padding,
    MessageBox, MessageBoxButtons, MessageBoxIcon, DialogResult,
    DockStyle, Orientation, View, SortOrder,
    TreeView, TreeViewAction,
    ListBox, DrawMode,
    ListView, ListViewItem, DrawItemState,
    TabControl, TabPage, TabAlignment, TabAppearance,
    ToolBar, ToolBarButton, ToolBarButtonStyle, ToolBarAppearance,
    ToolBarTextAlign,
    ToolTip,
    StatusBar,
    Cursor,
    HorizontalAlignment, ImageList,
    RichTextBox, RichTextBoxScrollBars, ControlStyles,
    HtmlDocument, SplitContainer,
    MainMenu, ContextMenu, MenuItem, Shortcut,
    Keys, Control,
    TextRenderer)

from System.Threading import Thread, ThreadStart, ApartmentState

from .. import version
from . import UIGlobal
from .FTConfig import FTConfig
from . import UICollections, FTCollections
from . import UIModulesList, UIReport
from .UIModuleInfo import ModuleInfoDialog
from .UIProjectChooser import ProjectChooser
from . import FTModules
from . import Help

from cdfutils.DotNet import (
    CustomMainMenu, 
    CustomToolBar, 
    ContextChecklist,
    SimpleContextMenu,
    )

# ------------------------------------------------------------------
# UI Messages & text

MESSAGE_Welcome = \
    "Welcome to FLExTools!"
MESSAGE_SelectProject = \
    "Select a project by clicking the Select Project button in the toolbar."
MESSAGE_SelectCollection = ""
MESSAGE_SelectCollectionToolbar = \
    "Select or create a collection by clicking the Collections button in the toolbar."
MESSAGE_SelectCollectionMenu = \
    "Select or create a collection by using the FlexTools | Manage collections menu, or pressing Ctrl-L."

# ------------------------------------------------------------------
class FTPanel(Panel):
    def __InitToolBar(self):

        global MESSAGE_SelectCollection
        
        # (Handler, Text, Image, Tooltip)
        ButtonListA = [
                      (self.__ChooseProject,
                       "Select Project",
                       "FLEX",
                       "Select the FieldWorks project to operate on"),
                      (self.__ManageCollections,
                       "Collections",
                       "folder-open",
                       "Manage and select a collection of modules"),
                      (self.ModuleInfo,
                       "Module Info",
                       "documents",
                       "Show the module documentation"),
                      #(None,
                      # "Configure",
                      # "applications",
                      # "Edit configuration parameters for this module"),
                      None, # Separator
                      ]
            
        if FTConfig.simplifiedRunOps:
            ButtonListB = [
                          (self.RunOneModify,
                           "Run",
                           "arrow-forward-!",
                           "Run the selected module"),
                          (self.RunAllModify,
                           "Run All",
                           "arrow-forward-double-!",
                           "Run all the modules")
                           ]
        else:
            ButtonListB = [
                          (self.RunOne,
                           "Run",
                           "arrow-forward",
                           "Run the selected module in preview mode"),
                          (self.RunAll,
                           "Run All",
                           "arrow-forward-double",
                           "Run all the modules in preview mode"),
                          (self.RunOneModify,
                           "Run (Modify)",
                           "arrow-forward-!",
                           "Run the selected module and allow changes to the project"),
                          (self.RunAllModify,
                           "Run All (Modify)",
                           "arrow-forward-double-!",
                           "Run all the modules and allow changes to the project")
                           ]
            
        if FTConfig.hideCollectionsButton:
            ButtonListA.pop(1)
            MESSAGE_SelectCollection = MESSAGE_SelectCollectionMenu
        else:
            MESSAGE_SelectCollection = MESSAGE_SelectCollectionToolbar
        

        return CustomToolBar(ButtonListA + ButtonListB,
                             UIGlobal.ToolbarIconParams)

    def __init__(self, 
                 moduleManager, 
                 listOfModules, 
                 reloadFunction, 
                 progressFunction,
                 changeCollectionFunction):
        Panel.__init__(self)

        self.Dock = DockStyle.Fill
        self.Font = UIGlobal.normalFont

        # -- Toolbar
        self.toolbar = self.__InitToolBar()
        
        self.__ManageCollectionsHandler = None

        # -- Module list and Report window
        self.moduleManager = moduleManager
        self.listOfModules = listOfModules
        self.reloadFunction = reloadFunction
        self.changeCollectionFunction = changeCollectionFunction

        self.modulesList = UIModulesList.ModulesList(self.moduleManager,
                                                     self.listOfModules)
        if FTConfig.simplifiedRunOps:
            self.modulesList.SetActivatedHandler(self.RunOneModify)
        else:
            self.modulesList.SetActivatedHandler(self.RunOne)

        self.reportWindow = UIReport.ReportWindow()

        self.startupToolTip = None

        startupTips = [MESSAGE_Welcome]
        if FTConfig.currentProject:
            self.UpdateProjectName()
        else:
            msg = MESSAGE_SelectProject
            startupTips.append(msg)

        if not self.listOfModules:
            msg = MESSAGE_SelectCollection
            startupTips.append(msg)

        for msg in startupTips:
            self.reportWindow.Report(msg)

        self.reportWindow.Report("Use the Run buttons to run modules.")

        if startupTips:
            self.startupToolTip = ToolTip()
            self.startupToolTip.IsBalloon = True
            self.startupToolTip.ToolTipTitle = "Getting started"
            self.startupToolTip.InitialDelay = 0
            self.startupToolTip.AutoPopDelay = 20000
            self.startupToolTip.SetToolTip(self.modulesList, "\n".join(startupTips))

        self.reportWindow.Reporter.RegisterProgressHandler(progressFunction)

        # -- The collection tabs 
        self.collectionsTabControl = TabControl()
        self.collectionsTabControl.Dock = DockStyle.Fill
        self.collectionsTabControl.Alignment = TabAlignment.Top
        self.collectionsTabControl.TabStop = False
        
        cm = SimpleContextMenu([(self.__OnMenuCloseTab, 
                                "Close current tab"),])
        self.collectionsTabControl.ContextMenu = cm
        
        self.ignoreTabChange = False
        self.collectionsTabControl.Selected += self.__OnTabSelected
        
        self.UpdateCollectionTabs()
        
        # -- Put it all together
        self.splitContainer1 = SplitContainer()
        self.splitContainer1.Dock = DockStyle.Fill
        self.splitContainer1.TabIndex = 1
        self.splitContainer1.SplitterWidth = UIGlobal.SPLITTER_WIDTH
        self.splitContainer1.SplitterDistance = 50
        self.splitContainer1.Orientation = Orientation.Horizontal
        self.splitContainer1.Panel1.Controls.Add(self.collectionsTabControl)
        self.splitContainer1.Panel2.Controls.Add(self.reportWindow)

        ## Add the main SplitContainer control to the panel.
        self.Controls.Add(self.splitContainer1)
        self.Controls.Add(self.toolbar)          # Last in takes space priority

    # ---- Toolbar button handlers ----

    def __ManageCollections(self):
        if self.__ManageCollectionsHandler:
            self.__ManageCollectionsHandler()

    def __ChooseProject(self):
        if self.__ChooseProjectHandler:
            self.__ChooseProjectHandler()

    def __Run(self, message, modules, modifyAllowed = False):
        # Reload the modules to make sure we're using the latest code.
        if self.reloadFunction: self.reloadFunction()

        if not FTConfig.currentProject:
            self.reportWindow.Reporter.Error("No project selected! Use the Select Project button in the toolbar.")
            return

        self.reportWindow.Clear()
        
        # The Shift key activates Modify for Enter key and double click.
        if not modifyAllowed:
            modifyAllowed = (Control.ModifierKeys == Keys.Shift)

        if modifyAllowed:
            # Only warn if some of the module(s) actually make modifications
            if FTConfig.warnOnModify and \
               any([self.moduleManager.CanModify(m) for m in modules]):
                dlgmsg = "Are you sure you want to make changes to the '%s' project? "\
                          "Please back up the project first."
                title = "Allow changes?"
                result = MessageBox.Show(dlgmsg % FTConfig.currentProject, title,
                                         MessageBoxButtons.YesNo,
                                         MessageBoxIcon.Question)
                if (result == DialogResult.No):
                    return
            if not FTConfig.simplifiedRunOps:
                message += " (Changes enabled)"

        self.reportWindow.Reporter.Info(message)
        self.reportWindow.Refresh()
        self.moduleManager.RunModules(FTConfig.currentProject,
                                      modules,
                                      self.reportWindow.Reporter,
                                      modifyAllowed)
        # Make sure the progress indicator is off
        self.reportWindow.Reporter.ProgressStop()

    def RunAll(self, modifyAllowed=False):
        self.__Run("Running all modules...",
                   self.listOfModules,
                   modifyAllowed)

    def RunOne(self, modifyAllowed=False):
        if self.modulesList.SelectedIndex >= 0:
            self.__Run("Running single module...",
                       [self.listOfModules[self.modulesList.SelectedIndex]],
                       modifyAllowed)

    def RunAllModify(self):
        self.RunAll(True)

    def RunOneModify(self):
        self.RunOne(True)

    # ---- Collections Tab handlers ----
    
    # Called when a tab is selected
    def __OnTabSelected(self, sender, event):
        
        if self.ignoreTabChange: return
        # Callback to parent Form to initiate refresh to new collection
        if self.changeCollectionFunction:
            if event.TabPage:
                self.changeCollectionFunction(event.TabPage.Text)
            else:
                self.changeCollectionFunction(None)
        
    # Called from the popup menu on the tabs
    def __OnMenuCloseTab(self, sender, event):

        currentTab = self.collectionsTabControl.SelectedTab
        
        # Remove the collection from the tab list
        # (FTConfig only supports assignment, so do this in two steps)
        tempCollections = FTConfig.collectionTabs
        index = tempCollections.index(currentTab.Text)
        tempCollections.remove(currentTab.Text)
        FTConfig.collectionTabs = tempCollections

        if len(FTConfig.collectionTabs):
            # Select the next tab to the left
            if index > 0: index = index - 1
            newCollection = FTConfig.collectionTabs[index]
        else:
            # All the tabs are closed
            newCollection = None

        if self.changeCollectionFunction:
            self.changeCollectionFunction(newCollection)

    # ---- Externally used methods ----

    def SetChooseProjectHandler(self, handler):
        self.__ChooseProjectHandler = handler

    def SetManageCollectionsHandler(self, handler):
        self.__ManageCollectionsHandler = handler

    def UpdateModuleList(self, listOfModules):
        if self.startupToolTip:
            self.startupToolTip.RemoveAll()
        self.listOfModules = listOfModules
        self.modulesList.UpdateAllItems(self.listOfModules)
        
    def UpdateCollectionTabs(self):
        self.ignoreTabChange = True     # Avoid nested TabChanged events
        
        # Clear out any old pages...
        self.collectionsTabControl.TabPages.Clear()
        
        if FTConfig.currentCollection:
            # ...and create them afresh           
            pages = [TabPage(name) for name in FTConfig.collectionTabs]
            self.collectionsTabControl.TabPages.AddRange(pages)
            
            # Activate the selected tab
            index = FTConfig.collectionTabs.index(FTConfig.currentCollection)
            currentTab = self.collectionsTabControl.TabPages[index]
            currentTab.Controls.Add(self.modulesList)
            currentTab.Focus()      # Removes dotted focus box from tab itself
            self.collectionsTabControl.SelectedTab = currentTab
        
        self.ignoreTabChange = False

        if FTConfig.currentCollection:
            self.reportWindow.Report("Collection '%s' selected." % FTConfig.currentCollection)
        else:
            self.reportWindow.Report(MESSAGE_SelectCollection)

    def UpdateProjectName(self):
        if self.startupToolTip:
            self.startupToolTip.RemoveAll()
        self.reportWindow.Report("Project '%s' selected." % FTConfig.currentProject)
        self.toolbar.UpdateButtonText(0, FTConfig.currentProject)
        
    def ModuleInfo(self):
        if self.modulesList.SelectedIndex >= 0:
            module = self.listOfModules[self.modulesList.SelectedIndex]
            moduleDocs = self.moduleManager.GetDocs(module)
            if moduleDocs:
                infoDialog = ModuleInfoDialog(moduleDocs)
                infoDialog.ShowDialog()

    def CopyReportToClipboard(self):
        self.reportWindow.CopyToClipboard()

    def ClearReport(self):
        self.reportWindow.Clear()

    def RefreshModules(self):
        self.modulesList.UpdateAllItems(self.listOfModules,
                                        keepSelection=True)

# ------------------------------------------------------------------

class FTMainForm (Form):

    def InitMainMenu(self, appMenu):

        # Handler, Text, Shortcut, Tooltip
        FlexToolsMenu = [(self.ChooseProject,
                          "Select Project...",
                          Shortcut.CtrlP,
                          "Select the FieldWorks project to operate on"),
                         (self.ManageCollections,
                          "Manage collections...",
                          Shortcut.CtrlL,
                          "Manage and select a collection of modules"),
                         (self.ModuleInfo,
                          "Module Information",
                          Shortcut.CtrlI,
                          "Show help information on the selected module"),
                         (self.ReloadModules,
                          "Re-load Modules",
                          Shortcut.F5,
                          "Re-import all modules"),
                         ## (TODO, "Preferences", Shortcut.CtrlP, None),
                         (self.Exit,  "Exit", Shortcut.CtrlQ, None)]
        if FTConfig.simplifiedRunOps:
            RunMenu = [(self.RunOneModify,
                        "Run Module",
                        Shortcut.CtrlR,
                        "Run the selected module"),
                       (self.RunAllModify,
                        "Run All Modules",
                        Shortcut.CtrlA,
                        "Run all the modules"),
                       ]
        else:
            RunMenu = [(self.RunOne,
                        "Run Module",
                        Shortcut.CtrlR,
                        "Run the selected module"),
                       (self.RunOneModify,
                        "Run Module (Modify Enabled)",
                        Shortcut.CtrlShiftR,
                        "Run the selected module and allow changes to the project"),
                       (self.RunAll,
                        "Run All Modules",
                        Shortcut.CtrlA,
                        "Run all the modules"),
                       (self.RunAllModify,
                        "Run All Modules (Modify Enabled)",
                        Shortcut.CtrlShiftA,
                        "Run all the modules and allow changes to the project"),
                       ]

        ReportMenu =    [(self.CopyToClipboard, 
                          "Copy to Clipboard", 
                          Shortcut.CtrlC,
                          "Copy the report contents to the clipboard"),
                         #(TODO, "Save...", Shortcut.CtrlS,
                         # "Save the current report to a file"),
                         (self.ClearReport, 
                          "Clear", 
                          Shortcut.CtrlX,
                          "Clear the current report")]

        HelpMenu =      [(Help.GeneralHelp,
                            "Help",
                            Shortcut.F1,
                            "Help on using FlexTools"),
                         (Help.ProgrammingHelp,
                            "Programming Help",
                            None,
                            "Help on how to program a FlexTools module"),
                         (Help.APIHelp,
                            "API Help",
                            None,
                            "Help on the Programming Interface"),
                         None,     # Separator
                         (Help.LaunchLCMBrowser,
                            "Launch Fieldworks LCMBrowser",
                            None,
                            "Open the Fieldworks LCMBrowser application"),
                         None,     # Separator
                         (Help.About,
                            "About",
                            None,
                            None)
                         ]

        MenuList = [("FLExTools", FlexToolsMenu),
                    ("Run", RunMenu),
                    ("Report", ReportMenu),
                    ("Help", HelpMenu)]

        if appMenu:
            MenuList.insert(3, appMenu)

        self.Menu = CustomMainMenu(MenuList)


    def __LoadModules(self):
        logger.debug("Loading modules")
        if not hasattr(self, "moduleManager"):
            self.moduleManager = FTModules.ModuleManager()
        errorList = self.moduleManager.LoadAll()
        if errorList:
            MessageBox.Show("\n".join(errorList), "Import Error!")
        if hasattr(self, "UIPanel"):
            self.UIPanel.RefreshModules()
            
    def __ChangeCollection(self, newCollection):
        # Called after editing collections in the Collections Manager
        # and when a new collections tab is selected in the UIPanel.
        # newCollection will be None if the last tab has been closed.
        FTConfig.currentCollection = newCollection
        
        if newCollection:
            # If the user selected/created a collection that is not in the
            # current tab list, then add it.
            if newCollection not in FTConfig.collectionTabs:
                newList = FTConfig.collectionTabs + [newCollection]
                FTConfig.collectionTabs = sorted(newList)
            
            # Refresh the list of modules
            try:
                listOfModules = self.collectionsManager.ListOfModules(
                                        FTConfig.currentCollection)
            except FTCollections.FTC_NameError:
                # The configuration value is bad... so reset everything.
                FTConfig.currentCollection = None
                FTConfig.collectionTabs = []
                listOfModules = []
        else:
            FTConfig.collectionTabs = []
            listOfModules = []

        self.UpdateStatusBar()

        self.UIPanel.UpdateModuleList(listOfModules)
        self.UIPanel.UpdateCollectionTabs()

    def __init__(self, appTitle=None, appMenu=None, appStatusbar=None):
        Form.__init__(self)
        self.ClientSize = UIGlobal.mainWindowSize
        if appTitle:
            self.Text = appTitle
        else:
            self.Text = f"flextoolslib {version}"

        # Initialise default configuration values
        if not FTConfig.currentCollection:
            FTConfig.currentCollection = "Examples"
        if not FTConfig.collectionTabs:
            FTConfig.collectionTabs = list((FTConfig.currentCollection,))
        elif FTConfig.currentCollection not in FTConfig.collectionTabs:
            newList = FTConfig.collectionTabs + [FTConfig.currentCollection]
            FTConfig.collectionTabs = sorted(newList)
            
        if FTConfig.warnOnModify == None:
            FTConfig.warnOnModify = True
        if FTConfig.stopOnError == None:
            FTConfig.stopOnError = False
        if FTConfig.simplifiedRunOps == None:
            FTConfig.simplifiedRunOps = False
        if FTConfig.disableDoubleClick == None:
            FTConfig.disableDoubleClick = False
        if FTConfig.hideCollectionsButton == None:
            FTConfig.hideCollectionsButton = True

        self.collectionsManager = FTCollections.CollectionsManager()

        self.__LoadModules()

        try:
            listOfModules = self.collectionsManager.ListOfModules(
                                            FTConfig.currentCollection)
        except FTCollections.FTC_NameError:
            # The configuration value is bad... so reset everything.
            FTConfig.currentCollection = None
            FTConfig.collectionTabs = []
            listOfModules = []

        self.Icon = Icon(UIGlobal.ApplicationIcon)

        self.InitMainMenu(appMenu)

        self.progressPercent = -1
        self.progressMessage = None
        self.StatusBar = StatusBar()
        self.statusbarCallback = appStatusbar
        self.UpdateStatusBar()

        self.UIPanel = FTPanel(self.moduleManager,
                               listOfModules,
                               self.__LoadModules,
                               self.__ProgressBar,
                               self.__ChangeCollection,
                               )
        self.UIPanel.SetChooseProjectHandler(self.ChooseProject)
        self.UIPanel.SetManageCollectionsHandler(self.ManageCollections)

        self.Controls.Add(self.UIPanel)
        self.Controls.Add(self.StatusBar)

    # ----
    def UpdateStatusBar(self):
        collectionText = f"Collection: {FTConfig.currentCollection}"

        if self.statusbarCallback:
            try:
                appText = self.statusbarCallback()
            except:
                appText = "ERROR with callback"
        else:
            appText = ""

        if self.progressPercent >= 0:
            msg = self.progressMessage if self.progressMessage else "Progress"
            progressText = "[%s: %i%%]" % (msg, self.progressPercent)
        else:
            progressText = ""
        
        newText = "   ".join((collectionText, appText, progressText))
        
        if self.StatusBar.Text != newText:
            self.StatusBar.Text = newText

    def __ProgressBar(self, val, max, msg=None):
        if max == 0: # Clear progress bar
            if self.progressPercent != -1:
                self.progressPercent = -1
                self.UpdateStatusBar()
            return

        newPercent = (val * 100) // max          # val = [0...max]
        refresh = False
        if msg != self.progressMessage:
            refresh = True
        elif newPercent != self.progressPercent:
            refresh = True
        if refresh:
            self.progressPercent = newPercent
            self.progressMessage = msg
            self.UpdateStatusBar()

    # ---- Menu handlers ----

    def Exit(self, sender=None, event=None):
        self.Close()

    def ManageCollections(self, sender=None, event=None):
        # Reload the modules to make sure we show the latest modules.
        self.__LoadModules()

        dlg = UICollections.CollectionsDialog(self.collectionsManager,
                                              self.moduleManager,
                                              FTConfig.currentCollection)
        dlg.ShowDialog()

        # Fall back to the currentCollection if there was no collection 
        # selected in the dialog.
        self.__ChangeCollection(dlg.activatedCollection or 
                                FTConfig.currentCollection)

    def ChooseProject(self, sender=None, event=None):
        dlg = ProjectChooser(FTConfig.currentProject)
        dlg.ShowDialog()
        if dlg.projectName != FTConfig.currentProject:
            FTConfig.currentProject = dlg.projectName
            self.UIPanel.UpdateProjectName()
            #self.UpdateStatusBar()  #Apr2023: removed project from statusbar

    def CopyToClipboard(self, sender, event):
        self.UIPanel.CopyReportToClipboard()

    def ClearReport(self, sender, event):
        self.UIPanel.ClearReport()

    def ModuleInfo(self, sender, event):
        self.UIPanel.ModuleInfo()

    def ReloadModules(self, sender, event):
        self.__LoadModules()

    def RunOne(self, sender, event):
        self.UIPanel.RunOne()
        
    def RunOneModify(self, sender, event):
        self.UIPanel.RunOneModify()
        
    def RunAll(self, sender, event):
        self.UIPanel.RunAll()
        
    def RunAllModify(self, sender, event):
        self.UIPanel.RunAllModify()



