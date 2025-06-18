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
#   Copyright Craig Farrow, 2010 - 2025
#

import logging
logger = logging.getLogger(__name__)

from flexlibs import OpenProjectInFW

import clr
import System

clr.AddReference("System.Drawing")
from System.Drawing import (Color, SystemColors, Point, PointF, Rectangle,
                            Size, Bitmap, Image, Icon,
                            SolidBrush, Pens, Font, FontStyle, FontFamily)

clr.AddReference("System.Windows.Forms")
from System.Windows.Forms import (
    Form,
    Panel, 
    MessageBox, MessageBoxButtons, MessageBoxIcon, DialogResult,
    DockStyle, Orientation,
    TabControl, TabPage, TabAlignment,
    ToolTip,
    StatusBar,
    SplitContainer,
    Keys, Control,
    )

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
    SimpleContextMenu,
    )

# ------------------------------------------------------------------
# UI Messages & text

MESSAGE_Welcome = \
    "Welcome to FLExTools!"
MESSAGE_SelectProject = \
    "Select a project by clicking the Select Project button in the toolbar."
MESSAGE_ProjectSelected = \
    "Project '%s' selected."
MESSAGE_CollectionSelected = \
    "Collection '%s' selected."
MESSAGE_SelectCollection = ""
MESSAGE_SelectCollectionToolbar = \
    "Select or create a collection by clicking the Collections button in the toolbar."
MESSAGE_SelectCollectionMenu = \
    "Select or create a collection by using the FlexTools | Manage Collections menu, or pressing Ctrl-L."
MESSAGE_RunButtons = \
    "Use the Run buttons to run modules."

# ------------------------------------------------------------------
class FTPanel(Panel):

    def __init__(self, 
                 moduleManager, 
                 listOfModules, 
                 reloadFunction, 
                 progressFunction,
                 changeCollectionFunction):
        Panel.__init__(self)

        self.Dock = DockStyle.Fill
        self.Font = UIGlobal.normalFont

        self.__ManageCollectionsHandler = None

        # -- Module list and Report window
        self.moduleManager = moduleManager
        self.listOfModules = listOfModules
        self.reloadFunction = reloadFunction
        self.changeCollectionFunction = changeCollectionFunction

        self.modulesList = UIModulesList.ModulesList(self.moduleManager,
                                                     self.listOfModules)
        if FTConfig.simplifiedRunOps:
            self.modulesList.SetActivatedHandler(self.RunModify)
        else:
            self.modulesList.SetActivatedHandler(self.Run)

        self.reportWindow = UIReport.ReportWindow()
        self.reportWindow.Reporter.RegisterProgressHandler(progressFunction)

        # -- Startup messages and getting started hint.
        self.reportWindow.Report(MESSAGE_Welcome)
        
        self.startupToolTip = None
        if FTConfig.currentProject:
            self.MsgProjectSelected()
        else:
            self.reportWindow.Report(MESSAGE_SelectProject)

            startupTips = [MESSAGE_Welcome]
            startupTips.append(MESSAGE_SelectProject)
            startupTips.append(MESSAGE_SelectCollection)
            startupTips.append(MESSAGE_RunButtons)

            self.startupToolTip = ToolTip()
            self.startupToolTip.IsBalloon = True
            self.startupToolTip.ToolTipTitle = "Getting started"
            self.startupToolTip.InitialDelay = 0
            self.startupToolTip.AutoPopDelay = 20000
            self.startupToolTip.SetToolTip(self.modulesList, 
                                           "\n".join(startupTips))

        # -- The collection tabs 
        self.collectionsTabControl = TabControl()
        self.collectionsTabControl.Dock = DockStyle.Fill
        self.collectionsTabControl.Alignment = TabAlignment.Top
        self.collectionsTabControl.TabStop = False
        
        cm = SimpleContextMenu([(self.__OnMenuCloseTab, 
                                "Close current collection tab"),])
        self.collectionsTabControl.ContextMenuStrip = cm
        
        self.ignoreTabChange = False
        self.collectionsTabControl.Selected += self.__OnTabSelected
        
        self.UpdateCollectionTabs()
        
        self.reportWindow.Report(MESSAGE_RunButtons)

        # -- Put it all together
        self.splitContainer1 = SplitContainer()
        self.splitContainer1.Dock = DockStyle.Fill
        self.splitContainer1.TabIndex = 1
        self.splitContainer1.SplitterWidth = UIGlobal.SPLITTER_WIDTH
        self.splitContainer1.SplitterDistance = 50
        self.splitContainer1.Orientation = Orientation.Horizontal
        self.splitContainer1.Panel1.Controls.Add(self.collectionsTabControl)
        self.splitContainer1.Panel2.Controls.Add(self.reportWindow)

        # Add the main SplitContainer control to the panel.
        self.Controls.Add(self.splitContainer1)

    # ---- Run actions ----

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

        if modifyAllowed and FTConfig.warnOnModify:
            # Only warn if some of the module(s) actually make modifications
            if any([self.moduleManager.CanModify(m) for m in modules]):
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
        if len(self.listOfModules) > 0:
            self.__Run("Running all modules...",
                       self.listOfModules,
                       modifyAllowed)

    def Run(self, modifyAllowed=False):
        selectedModules = list(self.modulesList.SelectedIndices)
        if len(selectedModules) > 0:
            if len(selectedModules) == 1:
                msg = "Running module..."
            else:
                msg = "Running selected modules..."

            modulesToRun = [m for i, m in enumerate(self.listOfModules) if i in selectedModules]
            self.__Run(msg,
                       modulesToRun,
                       modifyAllowed)

    def RunAllModify(self):
        self.RunAll(True)

    def RunModify(self):
        self.Run(True)

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
            self.reportWindow.Report(MESSAGE_CollectionSelected \
                                     % FTConfig.currentCollection)
        else:
            self.reportWindow.Report(MESSAGE_SelectCollection)

    def MsgProjectSelected(self):
        if self.startupToolTip:
            self.startupToolTip.RemoveAll()
        self.reportWindow.Report(MESSAGE_ProjectSelected % \
                                 FTConfig.currentProject)
        
    def ModuleInfo(self, sender=None, event=None):
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
                          Keys.Control | Keys.P,
                          "Select the FieldWorks project to operate on"),
                          (self.LaunchProject,
                          "Open Project in FieldWorks",
                          Keys.Control | Keys.Shift | Keys.P,
                          "Open the current project in FieldWorks"),
                         (self.ManageCollections,
                          "Manage Collections...",
                          Keys.Control | Keys.L,
                          "Manage and select a collection of modules"),
                         (self.ModuleInfo,
                          "Module Information",
                          Keys.Control | Keys.I,
                          "Show help information on the selected module"),
                         (self.ReloadModules,
                          "Re-load Modules",
                          Keys.F5,
                          "Re-import all modules"),
                         ## (TODO, "Preferences", Keys.Control | Keys.P, None),
                         #(self.Exit,
                          #"Exit",
                          #Keys.Control | Keys.Q,
                          #None)
        ]
        if FTConfig.simplifiedRunOps:
            RunMenu = [(self.RunModify,
                        "Run Module",
                        Keys.Control | Keys.R,
                        "Run the selected module"),
                       (self.RunAllModify,
                        "Run All Modules",
                        Keys.Control | Keys.A,
                        "Run all the modules"),
                       ]
        else:
            RunMenu = [(self.Run,
                        "Run Module(s)",
                        Keys.Control | Keys.R,
                        "Run the selected module(s)"),
                       (self.RunModify,
                        "Run Module(s) (Modify Enabled)",
                        Keys.Control | Keys.Shift | Keys.R,
                        "Run the selected module(s) and allow changes to the project"),
                       (self.RunAll,
                        "Run All Modules",
                        Keys.Control | Keys.A,
                        "Run all the modules"),
                       (self.RunAllModify,
                        "Run All Modules (Modify Enabled)",
                        Keys.Control | Keys.Shift | Keys.A,
                        "Run all the modules and allow changes to the project"),
                       ]

        ReportMenu =    [(self.CopyToClipboard,
                          "Copy to Clipboard",
                          Keys.Control | Keys.C,
                          "Copy the report contents to the clipboard"),
                         #(TODO, "Save...", Keys.Control | Keys.S,
                         # "Save the current report to a file"),
                         (self.ClearReport,
                          "Clear",
                          Keys.Control | Keys.X,
                          "Clear the current report")]

        HelpMenu =      [(Help.GeneralHelp,
                            "Help",
                            Keys.F1,
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
                            "Launch FieldWorks LCMBrowser",
                            None,
                            "Open the FieldWorks LCMBrowser application"),
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

        # Create the main menu
        
        # (.NET documentation says, "In addition to setting the 
        # MainMenuStrip property, you must Add the MenuStrip control 
        # to the Controls collection of the form.")
        self.MainMenuStrip = CustomMainMenu(MenuList)
        self.Controls.Add(self.MainMenuStrip)

        # Pre-calculate the menu items to disable when DisableRunAll is defined
        # for a collection.
        runallIndices = [i for i, m in enumerate(RunMenu)
                         if m[0] in (self.RunAll, self.RunAllModify)]
        runMenu = self.MainMenuStrip.Items[1]
        self.runallMenuItems = [runMenu.DropDownItems[i]
                                for i in runallIndices]


    def InitToolBar(self):

        global MESSAGE_SelectCollection
        
        # (Handler, Text, Image, Tooltip)
        ButtonListA = [
                      (self.ChooseProject,
                       "Select Project",
                       "Flex",
                       "Select the FieldWorks project to operate on"),
                      (self.ManageCollections,
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
                          (self.RunModify,
                           "Run",
                           "arrow-forward-!",
                           "Run the selected module(s)"),
                          (self.RunAllModify,
                           "Run All",
                           "arrow-forward-double-!",
                           "Run all the modules")
                           ]
        else:
            ButtonListB = [
                          (self.Run,
                           "Run",
                           "arrow-forward",
                           "Run the selected module(s) in preview mode"),
                          (self.RunAll,
                           "Run All",
                           "arrow-forward-double",
                           "Run all the modules in preview mode"),
                          (self.RunModify,
                           "Run (Modify)",
                           "arrow-forward-!",
                           "Run the selected module(s) and allow changes to the project"),
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
        
        ButtonList = ButtonListA + ButtonListB

        self.toolbar = CustomToolBar(ButtonList,
                                     UIGlobal.ToolbarIconParams)
        self.toolbar.Font = UIGlobal.normalFont
        self.Controls.Add(self.toolbar)

        # Pre-calculate the toolbar items to disable when DisableRunAll is defined
        # for a collection.
        runallIndices = [i for i, b in enumerate(ButtonList)
                         if b and b[0] in (self.RunAll, self.RunAllModify)]
        self.runallButtons = [self.toolbar.Items[i]
                              for i in runallIndices]

    def __LoadModules(self):
        logger.debug("Loading modules")
        if not hasattr(self, "moduleManager"):
            self.moduleManager = FTModules.ModuleManager()
        errorList = self.moduleManager.LoadAll()
        if errorList:
            MessageBox.Show("\n".join(errorList), "Import Error!")
        if hasattr(self, "UIPanel"):
            self.UIPanel.RefreshModules()
            
    def __EnsureTabsConsistent(self):
        # Several things could happen behind our backs (at startup
        # or after the user has used the Collections manager):
        #   - the current collection may not be in the tab list;
        #   - the tab list may contain out-dated collections
        #     (e.g. they may have been renamed or deleted)
        #   - the current collection may no longer exist;
        
        # Add the current collection in case it isn't in the tab list
        newTabs = set(FTConfig.collectionTabs + [FTConfig.currentCollection])
        # Filter out non-existing collections
        newList = sorted(newTabs.intersection(self.collectionsManager.Names()))
                          
        FTConfig.collectionTabs = newList
        logger.debug(f"Updated tab list: {newList}")
        
        # Check if the current collection is valid
        if FTConfig.currentCollection in FTConfig.collectionTabs:
            logger.debug(f"--> Collection: {FTConfig.currentCollection}")
        else:
            if FTConfig.collectionTabs:
                # Default to the first in the tab list
                FTConfig.currentCollection = FTConfig.collectionTabs[0]
                logger.debug(f"--> Current collection invalid: selecting first tab ({FTConfig.currentCollection})")
            else:
                # There's nothing to select
                FTConfig.currentCollection = None
                logger.debug(f"--> Current collection invalid and tab list is empty.")
            
    def __ChangeCollection(self, newCollection):
        # Called after editing collections in the Collections Manager
        # and when a new collections tab is selected in the UIPanel.
        # newCollection will be None if the last tab has been closed.
        FTConfig.currentCollection = newCollection
        
        if newCollection:
            # Update the collection tabs list according to any 
            # selection/renaming/deletion
            self.__EnsureTabsConsistent()

            # Refresh the list of modules if currentCollection is still 
            # set.
            if FTConfig.currentCollection:
                listOfModules = self.collectionsManager.ListOfModules(
                                        FTConfig.currentCollection)
            else:
                listOfModules = []
        else:
            FTConfig.collectionTabs = []
            listOfModules = []

        FTConfig.save()
        self.UpdateStatusBar()
        self.UpdateDisabledStates(False if not listOfModules else
                                  listOfModules.disableRunAll)

        self.UIPanel.UpdateModuleList(listOfModules)
        self.UIPanel.UpdateCollectionTabs()

    def __init__(self, appTitle=None, appMenu=None, appStatusbar=None):
        Form.__init__(self)
        self.ClientSize = UIGlobal.mainWindowSize
        if appTitle:
            self.Text = appTitle
        else:
            self.Text = f"flextoolslib {version}"

        self.Icon = Icon(UIGlobal.ApplicationIcon)

        # Initialise default configuration values
        if not FTConfig.currentCollection:
            FTConfig.currentCollection = "Examples"
        if not FTConfig.collectionTabs:
            FTConfig.collectionTabs = [FTConfig.currentCollection]

        if FTConfig.warnOnModify == None:
            FTConfig.warnOnModify = True
        if FTConfig.stopOnError is None:
            FTConfig.stopOnError = False
        if FTConfig.simplifiedRunOps is None:
            FTConfig.simplifiedRunOps = False
        if FTConfig.disableDoubleClick is None:
            FTConfig.disableDoubleClick = False
        if FTConfig.hideCollectionsButton is None:
            FTConfig.hideCollectionsButton = False

        self.collectionsManager = FTCollections.CollectionsManager()

        self.__EnsureTabsConsistent()
        
        self.__LoadModules()

        try:
            listOfModules = self.collectionsManager.ListOfModules(
                                            FTConfig.currentCollection)
        except FTCollections.FTC_NameError:
            # The configuration value is bad... so reset everything.
            FTConfig.currentCollection = None
            FTConfig.collectionTabs = []
            listOfModules = []

        FTConfig.save()

        # Main panel (modules' list & report window)
        self.UIPanel = FTPanel(self.moduleManager,
                               listOfModules,
                               self.__LoadModules,
                               self.__ProgressBar,
                               self.__ChangeCollection,
                               )

        self.Controls.Add(self.UIPanel)
        
        # Status bar
        self.progressPercent = -1
        self.progressMessage = None
        self.StatusBar = StatusBar()
        self.statusbarCallback = appStatusbar
        self.UpdateStatusBar()

        self.Controls.Add(self.StatusBar)
        
        # Toolbar
        self.InitToolBar()
        if FTConfig.currentProject:
            self.toolbar.UpdateButtonText(0, FTConfig.currentProject)

        # Main Menu
        self.InitMainMenu(appMenu)
        
        # Disable the RunAll menus and toolbar buttons if required
        self.UpdateDisabledStates(False if not listOfModules else
                                  listOfModules.disableRunAll)

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

    def UpdateDisabledStates(self, disableRunAll):
        for menu in self.runallMenuItems:
            menu.Enabled = not disableRunAll
        for button in self.runallButtons:
            button.Enabled = not disableRunAll

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

    # ---- Menu & Toolbar handlers ----

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
            FTConfig.save()
            self.toolbar.UpdateButtonText(0, FTConfig.currentProject)
            self.UIPanel.MsgProjectSelected()
            #self.UpdateStatusBar()  #Apr2023: removed project from statusbar

    def LaunchProject(self, sender=None, event=None):
        if FTConfig.currentProject:
            self.UIPanel.reportWindow.Report(
                f"Opening project '%s' in FieldWorks..." 
                % FTConfig.currentProject)

            OpenProjectInFW(FTConfig.currentProject)

    def CopyToClipboard(self, sender, event):
        self.UIPanel.CopyReportToClipboard()

    def ClearReport(self, sender, event):
        self.UIPanel.ClearReport()

    def ModuleInfo(self, sender, event):
        self.UIPanel.ModuleInfo()

    def ReloadModules(self, sender, event):
        self.__LoadModules()

    def Run(self, sender, event):
        self.UIPanel.Run()
        
    def RunModify(self, sender, event):
        self.UIPanel.RunModify()
        
    def RunAll(self, sender, event):
        self.UIPanel.RunAll()
        
    def RunAllModify(self, sender, event):
        self.UIPanel.RunAllModify()
