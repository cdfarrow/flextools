#
#   Project: FlexTools
#   Module:  UIModuleBrowser
#   Platform: .NET v2 Windows.Forms
#
#   UI for browsing and selecting Modules:
#    - Split panel with Module tree (folders & nodes) on left
#      and full information about the Module on right.
#   This is the bottom panel in the Collections Manager.
#
#   Craig Farrow
#   Oct 2009
#   v0.01
#

import os

from . import UIGlobal
from .FTModuleClass import *
from .UIModuleInfo import ModuleInfoPane

from System.Drawing import (
    Size,
    Font, FontStyle
    )

from System.Windows.Forms import (
    Application, 
    BorderStyle,
    Form,
    Panel,
    SplitContainer,
    TreeView, TreeViewAction,
    DockStyle, Orientation,
    ToolTip,
    KeyEventArgs, Keys, 
    )

class ModuleTree(TreeView):
    def __init__(self):
        TreeView.__init__(self)

      
        self.Dock = DockStyle.Fill
        self.ShowLines = False
        self.TabIndex = 0
        #self.BorderStyle = BorderStyle.None
        self.BackColor = UIGlobal.leftPanelColor
        self.FullRowSelect = True
        self.HideSelection = False    # Keep selected item grey when lost focus
        
        tooltip = ToolTip()
        tooltip.IsBalloon = True
        tooltip.SetToolTip(self, _("Double-click a module to add it to the current collection"))

    def SetSelectedHandler(self, handler):
        self.AfterSelect += handler

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
                if sender.SelectedNode.Nodes.Count == 0:
                    self.__ActivatedHandler(sender.SelectedNode.Name)


    def AddModuleName(self, moduleName):
        # The Key value is set to the full moduleName for looking up
        # the module, whereas the text displayed in the node has
        # the library name deleted.

        dotpos = moduleName.find(".")
        if dotpos > 0:
            libText = moduleName[:dotpos]
            moduleText = moduleName[dotpos+1:]
            
            idx = self.Nodes.IndexOfKey(libText)
            if idx >= 0:
                self.Nodes[idx].Nodes.Add(moduleName, moduleText)
            else:

                node = self.Nodes.Add(libText, libText)    # Key & Label
                node.NodeFont = Font(UIGlobal.normalFont,FontStyle.Italic)
                node.ForeColor = UIGlobal.accentColor
                node.Nodes.Add(moduleName, moduleText)
        else:
            self.Nodes.Add(moduleName, moduleName)


class ModuleBrowser(Panel):
    def __init__(self, moduleManager):
        Panel.__init__(self)
        self.moduleManager = moduleManager
        self.Dock = DockStyle.Fill

        self.moduleActivatedHandler = None
        
        # The infoPane contents is initialised through AfterSelect event
        # from ModuleTree
        self.infoPane = ModuleInfoPane()

        self.moduleTree = ModuleTree()
        for m in self.moduleManager.ListOfNames():
            self.moduleTree.AddModuleName(m)
        self.moduleTree.ExpandAll()
        self.selectedNode = ""
        self.moduleTree.SetSelectedHandler(self.TreeNodeSelected)
                        
        self.splitContainer1 = SplitContainer()
        self.splitContainer1.Dock = DockStyle.Fill
        self.splitContainer1.TabIndex = 1
        self.splitContainer1.SplitterWidth = UIGlobal.SPLITTER_WIDTH
        self.splitContainer1.SplitterDistance = 70
        self.splitContainer1.Orientation = Orientation.Vertical
        self.splitContainer1.Panel1.Controls.Add(self.moduleTree)
        self.splitContainer1.Panel2.Controls.Add(self.infoPane)
        
        ## Add the main SplitContainer control to the panel.
        self.Controls.Add(self.splitContainer1)

    def TreeNodeSelected(self, sender, event):
        if sender.SelectedNode.Nodes.Count != 0:
            self.infoPane.Text = "Library: "+sender.SelectedNode.Text
            self.selectedNode = ""
        else:
            # .Name == The Key given when adding to the TreeNodeCollection
            self.infoPane.SetFromDocs (
                self.moduleManager.GetDocs(sender.SelectedNode.Name))
            self.selectedNode = sender.SelectedNode.Name
        
    def SetActivatedHandler(self, handler):
        self.moduleTree.SetActivatedHandler(handler)


# ------------------------------------------------------------------
        
if __name__ == "__main__":
    import FTModules
    mm = FTModules.ModuleManager()
    mm.LoadAll()
    
    mb = ModuleBrowser(mm)
    
    form = Form()
    form.ClientSize = Size(500, 300)

    form.Text = "Test of Module Browser"
    form.Controls.Add(mb)
    Application.Run(form)
