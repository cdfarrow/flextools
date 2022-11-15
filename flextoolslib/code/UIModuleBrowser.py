#
#   Project: FlexTools
#   Module:  UIModuleBrowser
#   Platform: .NET v2 Windows.Forms
#
#   UI for browsing and selecting Modules:
#    - Split panel with Module tree (folders & nodes) on left
#      and full information about the Module on right.
#
#   TODO:
#
#   Craig Farrow
#   Oct 2009
#   v0.01
#

from __future__ import unicode_literals
from builtins import str

import os

import UIGlobal
from FTModuleClass import *

from System.Drawing import (Color, Point, Rectangle, Size, Bitmap,
                            Icon,
                            Font, FontStyle, FontFamily)
from System.Windows.Forms import (Application, BorderStyle, Button,
    Form, FormBorderStyle, Label,
    Panel, Screen,
    MessageBox, MessageBoxButtons, MessageBoxIcon, 
    DockStyle, Orientation, View, SortOrder,
    TreeView, TreeViewAction,
    ListView, ListViewItem, HorizontalAlignment, ImageList,
    ToolTip,
    KeyEventArgs, KeyPressEventArgs, Keys, 
    RichTextBox, HtmlDocument, SplitContainer )

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
        tooltip.SetToolTip(self, "Double-click a module to add it to the collection.") 

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
                node.ForeColor = Color.DarkSlateBlue
                node.Nodes.Add(moduleName, moduleText)
        else:
            self.Nodes.Add(moduleName, moduleName)


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
            self.HelpLink = moduleDocs[FTM_Help]
            
            s = self.SelectionStart
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


class ModuleBrowser(Panel):
    def __init__(self, modules):
        Panel.__init__(self)
        self.modules = modules
        self.Dock = DockStyle.Fill

        self.moduleActivatedHandler = None
        
        # The infoPane contents is initialised through AfterSelect event
        # from ModuleTree
        self.infoPane = ModuleInfoPane()

        self.moduleTree = ModuleTree()
        for m in self.modules.ListOfNames():
            self.moduleTree.AddModuleName(m)
        self.moduleTree.ExpandAll()
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
        ##print "Got TreeNodeSelected"
        if sender.SelectedNode.Nodes.Count != 0:
            ##print "This is a Library node"
            self.infoPane.Text = "Library: "+sender.SelectedNode.Text
            self.selectedNode = ""
        else:
            # .Name == The Key given when adding to the TreeNodeCollection
            #print "Node is:", sender.SelectedNode.Name
            self.infoPane.SetFromDocs (
                self.modules.GetDocs(sender.SelectedNode.Name))
            self.selectedNode = sender.SelectedNode.Name
        
    def SetActivatedHandler(self, handler):
        self.moduleTree.SetActivatedHandler(handler)



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
