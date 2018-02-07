#
#   Project: FlexTools
#   Module:  FLExTools
#   Platform: .NET v2 Windows.Forms (Python.NET 2.5)
#
#   Main FLexTools UI: loads straight in to configured database and
#    Collection.
#    - Split panel with Collections list above and Report results below.
#
#
#   Craig Farrow
#   Oct 2010
#

import codecs
import sys
sys.stdout = codecs.getwriter("utf-8")(sys.stdout)
import os
import traceback

import System

from System.Drawing import (Color, SystemColors, Point, PointF, Rectangle,
                            Size, Bitmap, Image, Icon,
                            SolidBrush, Pens, Font, FontStyle, FontFamily)

from System.Windows.Forms import (Application, BorderStyle, Button,
    Form, FormBorderStyle, Label,
    Panel, Screen, FixedPanel, Padding,
    MessageBox, MessageBoxButtons, MessageBoxIcon, DialogResult,
    DockStyle, Orientation, View, SortOrder,
    TreeView, TreeViewAction,
    ListBox, DrawMode,
    ListView, ListViewItem, DrawItemState,
    TabControl, TabPage, TabAlignment,
    ToolBar, ToolBarButton, ToolBarButtonStyle, ToolBarAppearance,
    ToolTip,
    StatusBar,
    HorizontalAlignment, ImageList,
    RichTextBox, RichTextBoxScrollBars, ControlStyles,
    HtmlDocument, SplitContainer,
    MainMenu, ContextMenu, MenuItem, Shortcut,
    Keys, Control,
    TextRenderer)

import Version
try:
    import FTPaths
    import UIGlobal
    import UICollections, FTCollections
    import UIModulesList, UIReport, UIModuleBrowser
    import UIDbChooser
    import FTModules
    import Help

except EnvironmentError, e:
    # EnvironmentError is used to communicate a known situation that can be handled,
    # typically with a restart.
    MessageBox.Show(e.message,
                    "FLExTools: Configuring",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Information)
    sys.exit(2)     # Signal a restart
                    
except Exception, e:
    MessageBox.Show("Error interfacing with Fieldworks:\n%s\n(This version of FLExTools supports Fieldworks versions %s - %s.)\nSee error.log for more details."
                    % (e.message, Version.MinFWVersion, Version.MaxFWVersion),
                    "FLExTools: Fatal Error",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Exclamation)
    print "Fatal exception during imports:\n%s" % traceback.format_exc()
    print "FLExTools %s" % Version.number
    sys.exit(1)

import CDFDotNetUtils
from CDFConfigStore import CDFConfigStore

# ------------------------------------------------------------------

class FTPanel(Panel):
    def __InitToolBar(self):

        # (Handler, Text, Image, Tooltip)
        ButtonList = [
                      (self.__ChooseDatabase,
                       "Choose Database",
                       "FLEX",
                       "Select the FieldWorks database to operate on"),
                      (self.__EditCollections,
                       "Collections",
                       "copy",
                       "Manage and select a collection of modules"),
                      None, # Separator
                      (self.__ShowInfo,
                       "Module Info",
                       "documents",
                       "Show the full module documentation"),
                      #(None,
                      # "Configure",
                      # "applications",
                      # "Edit configuration parameters for this module"),
                      None, # Separator
                      (self.RunOne,
                       "Run",
                       "arrow-forward",
                       "Run selected module in dry-run mode"),
                      (self.RunAll,
                       "Run All",
                       "arrow-forward-double",
                       "Run all modules in dry-run mode"),
                      (self.RunOneModify,
                       "Run (Modify)",
                       "arrow-forward-!",
                       "Run selected module with database changes enabled"),
                      (self.RunAllModify,
                       "Run All (Modify)",
                       "arrow-forward-double-!",
                       "Run all modules with database changes enabled")
                       ]

        return CDFDotNetUtils.CDFToolBar(ButtonList,
                                         UIGlobal.ToolbarIconParams)
        
    def __init__(self, moduleManager, dbName, listOfModules, reloadFunction, progressFunction):
        Panel.__init__(self)

        self.Dock = DockStyle.Fill
        self.Font = UIGlobal.normalFont

        # -- Toolbar
        self.toolbar = self.__InitToolBar()
        self.__EditCollectionsHandler = None

        # -- Module list and Report window
        self.moduleManager = moduleManager
        self.dbName = dbName        
        self.listOfModules = listOfModules
        self.reloadFunction = reloadFunction

        self.modulesList = UIModulesList.ModulesList(self.moduleManager,
                                                     self.listOfModules)
        self.modulesList.SetActivatedHandler(self.RunOne)
            
        self.reportWindow = UIReport.ReportWindow()
        
        startupTips = []
        if dbName:
            self.UpdateDatabaseName(dbName)
        else:
            msg = "Choose a database by clicking the Choose Database button in the toolbar."
            startupTips.append(msg)
            
        if not self.listOfModules:
            msg = "Choose or create a collection by clicking the Collections button in the toolbar."
            startupTips.append(msg)

        for msg in startupTips:
            self.reportWindow.Report(msg)

        self.reportWindow.Report("Use the Run buttons to run Modules.")
        
        if startupTips:
            self.startupTip = ToolTip()
            self.startupTip.IsBalloon = True
            self.startupTip.ToolTipTitle = "Getting started"
            self.startupTip.InitialDelay = 0
            self.startupTip.AutoPopDelay = 20000
            self.startupTip.SetToolTip(self.modulesList, "\n".join(startupTips)) 
        else:
            self.startupTip = None

            
        self.reportWindow.Reporter.RegisterProgressHandler(progressFunction)
               
        # -- Put it all together
        self.splitContainer1 = SplitContainer()
        self.splitContainer1.Dock = DockStyle.Fill
        self.splitContainer1.TabIndex = 1
        self.splitContainer1.SplitterWidth = UIGlobal.SPLITTER_WIDTH
        self.splitContainer1.SplitterDistance = 50
        self.splitContainer1.Orientation = Orientation.Horizontal
        self.splitContainer1.Panel1.Controls.Add(self.modulesList)
        self.splitContainer1.Panel2.Controls.Add(self.reportWindow)

        ## Add the main SplitContainer control to the panel.
        self.Controls.Add(self.splitContainer1)
        self.Controls.Add(self.toolbar)          # Last in takes space priority

        
        
    # ---- Toolbar button handlers ----
    
    def __EditCollections(self):
        if self.startupTip:
            self.startupTip.RemoveAll()

        if self.__EditCollectionsHandler:
            self.__EditCollectionsHandler()
        
    def __ChooseDatabase(self):
        if self.startupTip:
            self.startupTip.RemoveAll()
            
        if self.__ChooseDatabaseHandler:
            self.__ChooseDatabaseHandler()
        
    def __ShowInfo(self):
        if self.modulesList.SelectedIndex >= 0:
            module = self.listOfModules[self.modulesList.SelectedIndex]
            moduleDocs = self.moduleManager.GetDocs(module)
            if moduleDocs:
                infoDialog = UIModuleBrowser.ModuleInfoDialog(moduleDocs)
                infoDialog.ShowDialog()


    def __Run(self, message, modules, modifyDB = False):
        # Reload the Modules to make sure we're using the latest code.
        if self.reloadFunction: self.reloadFunction()
        
        if not self.dbName:
            self.reportWindow.Reporter.Error("No database selected! Use the Database button in the toolbar.")
            return

        if not modifyDB:
            modifyDB = (Control.ModifierKeys == Keys.Shift)

        self.reportWindow.Clear()
        
        if modifyDB:
            dlgmsg = "Are you sure you want to make changes to the '%s' database? "\
                      "(Please backup the project first.)"
            title = "Confirm allow changes"
            result = MessageBox.Show(dlgmsg % self.dbName, title,
                                     MessageBoxButtons.YesNo,
                                     MessageBoxIcon.Question)
            if (result == DialogResult.No):
                return

            message += " (Changes enabled)"
            
        self.reportWindow.Reporter.Info(message)
        self.reportWindow.Refresh()
        self.moduleManager.RunModules(self.dbName,
                                      modules,
                                      self.reportWindow.Reporter,
                                      modifyDB)
        # Make sure the progress indicator is off
        self.reportWindow.Reporter.ProgressStop()   

            
    def RunAll(self, modify=False):
        self.__Run("Running all modules...",
                   self.listOfModules,
                   modify)
        
    def RunOne(self, modify=False):
        if self.modulesList.SelectedIndex >= 0:
            self.__Run("Running single module...",
                       [self.listOfModules[self.modulesList.SelectedIndex]],
                       modify)

    def RunAllModify(self):
        self.RunAll(True)

    def RunOneModify(self):
        self.RunOne(True)
        
    # ---- Externally used methods ----

    def SetChooseDatabaseHandler(self, handler):
        self.__ChooseDatabaseHandler = handler
        
    def SetEditCollectionsHandler(self, handler):
        self.__EditCollectionsHandler = handler
        
    def UpdateModuleList(self, collectionName, listOfModules):
        self.listOfModules = listOfModules
        self.modulesList.UpdateAllItems(self.listOfModules)
        self.reportWindow.Report("Collection '%s' selected." % collectionName)

    def UpdateDatabaseName(self, newDatabaseName):
        self.dbName = newDatabaseName
        self.reportWindow.Report("Database '%s' selected." % self.dbName)
        self.toolbar.UpdateButtonText(0, self.dbName)

    def RefreshModules(self):
        self.modulesList.UpdateAllItems(self.listOfModules,
                                        keepSelection=True)

        

# ------------------------------------------------------------------

class FTMainForm (Form):

    def InitMainMenu(self):

        # Handler, Text, Shortcut, Tooltip
        FlexToolsMenu = [(self.ChooseDatabase,
                          "Choose Database...",
                          Shortcut.CtrlD,
                          "Select the FieldWorks database to operate on"),
                         (self.EditCollections,
                          "Collections...",
                          Shortcut.CtrlL,
                          "Manage and select a collection of modules"),
                         (self.ReloadModules,
                          "Re-load Modules",
                          Shortcut.F5,
                          "Re-import all modules"),
                         ## (None, "Preferences", Shortcut.CtrlP, None),
                         (self.Exit,  "Exit", Shortcut.CtrlQ, None)]

        RunMenu =       [(self.RunOne,
                          "Run Module",
                          Shortcut.CtrlR,
                          "Run the selected Module"),
                         (self.RunOneModify,
                          "Run Module (Modify enabled)",
                          Shortcut.CtrlShiftR,
                          "Run the selected Module allowing database changes"),
                         (self.RunAll,
                          "Run All Modules",
                          Shortcut.CtrlA,
                          "Run all modules"),
                         (self.RunAllModify,
                          "Run All Module (Modify enabled)",
                          Shortcut.CtrlShiftA,
                          "Run all modules allowing database changes"),]
        
        ReportMenu =    [(self.CopyToClipboard, "Copy to clipboard", Shortcut.CtrlC,
                          "Copies current report to the clipboard"),
                         #(None, "Save...", Shortcut.CtrlS,
                         # "Save the current report to a file"),
                         (self.ClearReport, "Clear", Shortcut.CtrlX,
                          "Clear the current report")]

        HelpMenu =      [(Help.GeneralHelp, "Help", Shortcut.F1,
                            "Help on using FlexTools"),
                         (Help.ProgrammingHelp, "Programming Help", Shortcut.None,
                            "Help on how to prgram a FlexTools Module"),
                         (Help.APIHelp, "API Help", Shortcut.None,
                            "Help on the Programming Interface"),
                         None,     # Separator
                         (Help.LaunchFDOBrowser, "Launch FDOBrowser", Shortcut.None,
                            "Open the Fieldworks FDOBrowser application"),
                         None,     # Separator
                         (Help.About, "About", Shortcut.None, None)
                         ]


        MenuList = [("FLExTools", FlexToolsMenu),
                    ("Run", RunMenu),
                    ("Report", ReportMenu),
                    ("Help", HelpMenu)]


        self.Menu = CDFDotNetUtils.CDFMainMenu(MenuList)


    def __LoadModules(self):
        if not hasattr(self, "moduleManager"):
            self.moduleManager = FTModules.ModuleManager()
        errorList = self.moduleManager.LoadAll()
        if errorList:
            MessageBox.Show("\n".join(errorList), "Import Error!")
        if hasattr(self, "UIPanel"):
            self.UIPanel.RefreshModules()
        
    def __init__(self):
        Form.__init__(self)
        self.ClientSize = Size(700, 500)
        self.Text = "FLExTools " + Version.number

        ## Get configurables - current DB, current collection
        self.configuration = CDFConfigStore(FTPaths.CONFIG_PATH)

        self.collectionsManager = FTCollections.CollectionsManager()

        self.__LoadModules()
        
        try:
            listOfModules = self.collectionsManager.ListOfModules(
                                   self.configuration.currentCollection)
        except FTCollections.FTC_NameError:
            # The configuration value is bad...
            self.configuration.currentCollection = None
            listOfModules = []

        self.Icon = Icon(UIGlobal.ApplicationIcon)
        
        self.InitMainMenu()

        self.progressPercent = -1
        self.progressMessage = None
        self.StatusBar = StatusBar()
        self.__UpdateStatusBar()

        self.UIPanel = FTPanel(self.moduleManager,
                               self.configuration.currentDatabase,
                               listOfModules,
                               self.__LoadModules,
                               self.__ProgressBar
                               )
        self.UIPanel.SetChooseDatabaseHandler(self.ChooseDatabase)
        self.UIPanel.SetEditCollectionsHandler(self.EditCollections)
        self.FormClosed += self.__OnFormClosed

        self.Controls.Add(self.UIPanel)
        self.Controls.Add(self.StatusBar)
        
    def __OnFormClosed(self, sender, event):
        # Event triggered when self.Close() is called.
        del self.configuration  # Save data by deleting ConfigStore object
        pass

    # ----
    def __UpdateStatusBar(self):
        if self.progressPercent >= 0:
            msg = self.progressMessage if self.progressMessage else "Progress"
            progressText = "[%s: %i%%]" % (msg, self.progressPercent)
        else:
            progressText = ""
        self.StatusBar.Text = "Collection: '%s'   Database: '%s'   %s" %\
             (self.configuration.currentCollection,
              #self.configuration.currentServer
              self.configuration.currentDatabase,
              progressText)

    def __ProgressBar(self, val, max, msg=None):
        if max == 0: # Clear progress bar
            if self.progressPercent <> -1:
                self.progressPercent = -1
                self.__UpdateStatusBar()
            return
            
        newPercent = (val * 100) / max          # val = [0...max]
        refresh = False
        if msg <> self.progressMessage:
            refresh = True
        elif newPercent <> self.progressPercent:
            refresh = True
        if refresh:
            self.progressPercent = newPercent
            self.progressMessage = msg
            self.__UpdateStatusBar()
            

    # ---- Menu handlers ----
    
    def Exit(self, sender=None, event=None):
        self.Close()  
        
    def EditCollections(self, sender=None, event=None):
        # Reload the Modules to make sure we show the latest modules.
        self.__LoadModules()

        dlg = UICollections.CollectionsDialog(self.collectionsManager,
                                              self.moduleManager,
                                              self.configuration.currentCollection)
        dlg.ShowDialog()
        self.configuration.currentCollection = dlg.activatedCollection
        self.__UpdateStatusBar()
            
        # Always refresh the list in case the current one was changed.
        try:
            listOfModules = self.collectionsManager.ListOfModules(
                                    self.configuration.currentCollection)
        except FTCollections.FTC_NameError:
            # The configuration value is bad or None...
            self.configuration.currentCollection = None
            listOfModules = []
        self.UIPanel.UpdateModuleList(self.configuration.currentCollection,
                                      listOfModules)

    def ChooseDatabase(self, sender=None, event=None):
        dlg = UIDbChooser.DatabaseChooser(self.configuration.currentDatabase)
        dlg.ShowDialog()
        if dlg.databaseName <> self.configuration.currentDatabase:
            self.configuration.currentDatabase = dlg.databaseName
            self.UIPanel.UpdateDatabaseName(dlg.databaseName)
            self.__UpdateStatusBar()

##        # Use FW Open Database dialog; This is rather broken
##        # (TODO: Server option not supported yet:
##        # I haven't found out how to open the db on a server, yet:
##        # Look in FDOBrowser::BrowserProjectId)
##        dbServer, dbPath = FDO.ChooseDatabaseDialog()
##        if dbPath:
##            dataDir = FLExRegUtil.GetFWDirs()[1]
##            if os.path.commonprefix([dataDir, dbPath]) == dataDir:
##                dbName = os.path.splitext(os.path.basename(dbPath))[0]
##            else:
##                dbName = dbPath
##            self.configuration.currentServer = dbServer
##            self.configuration.currentDatabase = dbName
##            self.UIPanel.UpdateDatabaseName(dbName)
##            self.__UpdateStatusBar()

    def CopyToClipboard(self, sender, event):
        self.UIPanel.reportWindow.CopyToClipboard()

    def ClearReport(self, sender, event):
        self.UIPanel.reportWindow.Clear()

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

# ------------------------------------------------------------------


if __name__ == "__main__":

    form = FTMainForm()

    Application.Run(form)


