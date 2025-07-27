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

clr.AddReference("System.Windows.Forms")
from System.Windows.Forms import (
    Form,
    Panel, 
    MessageBox, MessageBoxButtons, MessageBoxIcon, DialogResult,
    DockStyle, Orientation,
    ToolStripButton,
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
# Localisation

import gettext

if FTConfig.UILanguage not in UIGlobal.ALL_LOCALES:
    FTConfig.UILanguage = UIGlobal.DEFAULT_LOCALE
    
# fallback = True makes it silently fall back to the original strings if
# the language code is invalid (i.e. the .mo file isn't found).
translator = gettext.translation('flextools', 
                                 UIGlobal.LOCALES_PATH, 
                                 languages=[FTConfig.UILanguage],
                                 fallback = True)
translator.install()

# ------------------------------------------------------------------
# UI Messages & text

MESSAGE_Welcome = \
    _("Welcome to FLExTools!")
MESSAGE_SelectProject = \
    _("Select a project by clicking the 'Select project' button in the toolbar.")
MESSAGE_ProjectSelected = \
    _("Project '{}' selected.")
MESSAGE_CollectionSelected = \
    _("Collection '{}' selected.")
MESSAGE_SelectCollection = ""
MESSAGE_SelectCollectionToolbar = \
    _("Select or create a collection by clicking the 'Collections' button in the toolbar.")
MESSAGE_SelectCollectionMenu = \
    _("Select or create a collection by using the 'FlexTools | Manage collections' menu, or pressing Ctrl-L.")
MESSAGE_RunButtons = \
    _("Use the Run buttons to run modules.")

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
            self.startupToolTip.ToolTipTitle = _("Getting started")
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
                                _("Close current collection tab")),])
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
            self.reportWindow.Reporter.Error(_("No project selected! Use the 'Select project' button in the toolbar."))
            return

        self.reportWindow.Clear()
        
        # The Shift key activates Modify for Enter key and double click.
        if not modifyAllowed:
            modifyAllowed = (Control.ModifierKeys == Keys.Shift)

        if modifyAllowed and FTConfig.warnOnModify:
            # Only warn if some of the module(s) actually make modifications
            if any([self.moduleManager.CanModify(m) for m in modules]):
                dlgmsg = _("Are you sure you want to make changes to the '{}' project? "\
                          "Please back up the project first.")
                title = _("Allow changes?")
                result = MessageBox.Show(dlgmsg.format(FTConfig.currentProject), 
                                         title,
                                         MessageBoxButtons.YesNo,
                                         MessageBoxIcon.Question)
                if (result == DialogResult.No):
                    return
            if not FTConfig.simplifiedRunOps:
                # NOTE: Keep the space at the beginning if your language uses spaces.
                message += _(" (Changes enabled)")
       
        self.reportWindow.Reporter.Info(message)
        self.reportWindow.Refresh()
        
        # Freeze our UI for when a module does its own UI (e.g. FLExTrans)
        self.Parent.Enabled = False
        self.moduleManager.RunModules(FTConfig.currentProject,
                                      modules,
                                      self.reportWindow.Reporter,
                                      modifyAllowed)
        # Make sure the progress indicator is off
        self.reportWindow.Reporter.ProgressStop()
        self.Parent.Enabled = True

    def RunAll(self, modifyAllowed=False):
        if len(self.listOfModules) > 0:
            self.__Run(_("Running all modules..."),
                       self.listOfModules,
                       modifyAllowed)

    def Run(self, modifyAllowed=False):
        selectedModules = list(self.modulesList.SelectedIndices)
        if len(selectedModules) > 0:
            if len(selectedModules) == 1:
                msg = _("Running module...")
            else:
                msg = _("Running selected modules...")

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
            self.reportWindow.Report(MESSAGE_CollectionSelected.
                                    format(FTConfig.currentCollection))
        else:
            self.reportWindow.Report(MESSAGE_SelectCollection)

    def MsgProjectSelected(self):
        if self.startupToolTip:
            self.startupToolTip.RemoveAll()
        self.reportWindow.Report(MESSAGE_ProjectSelected.
                                    format(FTConfig.currentProject))
        
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
                          # NOTE: Menu item
                          _("Select project"),
                          Keys.Control | Keys.P,
                          _("Select the FieldWorks project to operate on")
                         ),
                         (self.LaunchProject,
                          # NOTE: Menu item
                          _("Open project in FieldWorks"),
                          Keys.Control | Keys.Shift | Keys.P,
                          _("Open the current project in FieldWorks")
                         ),
                         (self.ManageCollections,
                          # NOTE: Menu item
                          _("Manage collections"),
                          Keys.Control | Keys.L,
                          _("Manage and select a collection of modules")
                         ),
                         (self.ModuleInfo,
                          # NOTE: Menu item
                          _("Module information"),
                          Keys.Control | Keys.I,
                          _("Show help information on the selected module")
                         ),
                         (self.ReloadModules,
                          # NOTE: Menu item
                          _("Re-load modules"),
                          Keys.F5,
                          _("Re-import all modules")
                         ),
                         ## (TODO, _("Settings)", None, None),
                         #(self.Exit,
                          #_("Exit"),
                          #Keys.Control | Keys.Q,
                          #None)
                        ]
        if FTConfig.simplifiedRunOps:
            RunMenu = [(self.RunModify,
                        # NOTE: Menu item
                        _("Run module"),
                        Keys.Control | Keys.R,
                        _("Run the selected module")
                       ),
                       (self.RunAllModify,
                        # NOTE: Menu item
                        _("Run all modules"),
                        Keys.Control | Keys.A,
                        _("Run all the modules")
                       ),
                      ]
        else:
            RunMenu = [(self.Run,
                        # NOTE: Menu item
                        _("Run module(s)"),
                        Keys.Control | Keys.R,
                        _("Run the selected module(s)")
                       ),
                       (self.RunModify,
                        # NOTE: Menu item
                        _("Run module(s) (Modify enabled)"),
                        Keys.Control | Keys.Shift | Keys.R,
                        _("Run the selected module(s) and allow changes to the project")
                       ),
                       (self.RunAll,
                        # NOTE: Menu item
                        _("Run all modules"),
                        Keys.Control | Keys.A,
                        _("Run all the modules")
                       ),
                       (self.RunAllModify,
                        # NOTE: Menu item
                        _("Run all modules (Modify enabled)"),
                        Keys.Control | Keys.Shift | Keys.A,
                        _("Run all the modules and allow changes to the project")
                       ),
                      ]
        ReportMenu =    [(self.CopyToClipboard,
                          # NOTE: Menu item
                          _("Copy to clipboard"),
                          Keys.Control | Keys.C,
                          _("Copy the report contents to the clipboard")
                         ),
                         #(TODO, _("Save..."), Keys.Control | Keys.S,
                         # _("Save the current report to a file")),
                         (self.ClearReport,
                          # NOTE: Menu item
                          _("Clear"),
                          Keys.Control | Keys.X,
                          _("Clear the current report")
                         ),
                        ]
                        
        HelpMenu =      [(Help.GeneralHelp,
                          # NOTE: Menu item
                          _("Help"),
                          Keys.F1,
                          _("Help on using FlexTools")
                         ),
                         (Help.ProgrammingHelp,
                          # NOTE: Menu item
                          _("Programming help"),
                          None,
                          _("Help on how to program a FlexTools module")
                         ),
                         (Help.APIHelp,
                          # NOTE: Menu item
                          _("API help"),
                          None,
                          ("Help on the Programming Interface")
                         ),
                         None,     # Separator
                         (Help.LaunchLCMBrowser,
                          # NOTE: Menu item
                          _("Launch LCMBrowser"),
                          None,
                          _("Open the FieldWorks LCMBrowser application")
                         ),
                         None,     # Separator
                         (Help.About,
                          # NOTE: Menu item
                          _("About"),
                          None,
                          None
                         ),
                        ]

        MenuList = [
                    # NOTE: Menu title
                    (_("FLExTools"), FlexToolsMenu),
                    # NOTE: Menu title
                    (_("Run"), RunMenu),
                    # NOTE: Menu title
                    (_("Report"), ReportMenu),
                    # NOTE: Menu title
                    (_("Help"), HelpMenu)]

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
                          # NOTE: Toolbar item
                          _("Select project"),
                          "Flex",
                          _("Select the FieldWorks project to operate on")),
                       (self.ManageCollections,
                          # NOTE: Toolbar item
                         _("Collections"),
                         "folder-open",
                         _("Manage and select a collection of modules")),
                       (self.ModuleInfo,
                          # NOTE: Toolbar item
                         _("Module info"),
                         "documents",
                         _("Show the module documentation")),
                       #(None,
                       # _("Configure"),
                       # "applications",
                       # _("Edit configuration parameters for this module")),
                        None, # Separator
                       ]
            
        if FTConfig.simplifiedRunOps:
            ButtonListB = [
                           (self.RunModify,
                              # NOTE: Toolbar item
                              _("Run"),
                              "arrow-forward-!",
                              _("Run the selected module(s)")),
                           (self.RunAllModify,
                              # NOTE: Toolbar item
                              _("Run all"),
                              "arrow-forward-double-!",
                              _("Run all the modules"))
                          ]
        else:
            ButtonListB = [
                           (self.Run,
                              # NOTE: Toolbar item
                              _("Run"),
                              "arrow-forward",
                              _("Run the selected module(s) in preview mode")),
                           (self.RunAll,
                              # NOTE: Toolbar item
                              _("Run all"),
                              "arrow-forward-double",
                              _("Run all the modules in preview mode")),
                           (self.RunModify,
                              # NOTE: Toolbar item
                              _("Run (Modify)"),
                              "arrow-forward-!",
                              _("Run the selected module(s) and allow changes to the project")),
                           (self.RunAllModify,
                              # NOTE: Toolbar item
                              _("Run all (Modify)"),
                              "arrow-forward-double-!",
                              _("Run all the modules and allow changes to the project"))
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
            MessageBox.Show("\n".join(errorList), _("Import Error!"))
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

        if FTConfig.simplifiedRunOps:
            self.ClientSize = UIGlobal.mainWindowSizeNarrow
        else:
            self.ClientSize = UIGlobal.mainWindowSizeNormal
            
        if appTitle:
            self.Text = appTitle
        else:
            self.Text = f"flextoolslib {version}"

        self.Icon = UIGlobal.ApplicationIcon

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
        collectionText = _("Collection: {}").format(FTConfig.currentCollection)

        if self.statusbarCallback:
            try:
                appText = self.statusbarCallback()
            except:
                appText = "ERROR with callback"
        else:
            appText = ""

        if self.progressPercent >= 0:
            msg = self.progressMessage if self.progressMessage else _("Progress")
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
                _("Opening project '{}' in FieldWorks...").format(FTConfig.currentProject))

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

        # Hack to make the blue toolbar button highlight go away.
        # This only affects modules that open another UI (such as
        # the FLExTrans tools.)
        if isinstance(sender, ToolStripButton):
            sender.Visible = False
            sender.Visible = True

    def RunModify(self, sender, event):
        self.UIPanel.RunModify()
        
        # Hack to make the blue toolbar button highlight go away.
        # This only affects modules that open another UI (such as
        # the FLExTrans tools.)
        if isinstance(sender, ToolStripButton):
            sender.Visible = False
            sender.Visible = True
        
    def RunAll(self, sender, event):
        self.UIPanel.RunAll()

    def RunAllModify(self, sender, event):
        self.UIPanel.RunAllModify()
