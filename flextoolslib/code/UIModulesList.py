#
#   Project: FlexTools
#   Module:  UIModulesList
#   Platform: .NET v2 Windows.Forms (Python.NET 2.5)
#
#   A custom list for selecting the modules in the main FLexTools UI.
#
#
#   Copyright Craig Farrow, 2010 - 2022
#

from . import UIGlobal
from .FTConfig import FTConfig
from .FTModuleClass import *

from System import String

from System.Collections.Generic import List

from System.Drawing import (Color, SystemColors, Point, PointF, Rectangle,
                            Size, Bitmap, Image, Icon, SystemIcons,
                            SolidBrush, Pens, Font, FontStyle, FontFamily)

from System.Windows.Forms import (
    ListBox, SelectionMode, DrawMode,
    Button,
    DockStyle, Orientation, View, SortOrder,
    HorizontalAlignment, ImageList,
    DrawItemState, DrawItemEventArgs,
    KeyEventArgs, KeyPressEventArgs, Keys,
    TextRenderer)

# ------------------------------------------------------------------


class ModulesList(ListBox):
    SPACING = 1
    ICON_SPACE = 34

    def __init__(self, moduleManager, contents):
        ListBox.__init__(self)

        self.moduleManager = moduleManager

        # behaviour
        self.LabelEdit = False
        self.SelectionMode = SelectionMode.MultiExtended

        # appearance
        self.Dock = DockStyle.Fill
        self.ScrollAlwaysVisible = True
        self.TabIndex = 0
        self.HideSelection = False    # Keep selected item grey when lost focus

        self.textBrush = SolidBrush(SystemColors.WindowText)
        self.icon = Bitmap(UIGlobal.ModuleIcon)

        self.DrawMode = DrawMode.OwnerDrawVariable
        self.DrawItem += self.OnDrawItem
        self.MeasureItem += self.OnMeasureItem

        self.UpdateAllItems(contents)

    # ---- Custom drawing methods ----

    def __countLines(self, s):
        return len(s.split("\n"))

    def OnMeasureItem(self, sender, e):
        if e.Index < 0: return
        textHeight = self.Font.Height * self.__countLines(sender.Items[e.Index])
        e.ItemHeight = textHeight + 2 + self.SPACING # extra for separator line

    def OnDrawItem(self, sender, e):
        if e.Index < 0: return

        g = e.Graphics

        ## Custom draw... an icon and multi-line text

        # Use our own size to preserve the border line
        myBounds = e.Bounds
        myBounds.Height -= self.SPACING

        imageRect = myBounds.MemberwiseClone()
        imageRect.Inflate(-1,-1)
        imageRect.Width = self.icon.Width
        imageRect.X += (self.ICON_SPACE - self.icon.Width) // 2
        imageRect.Y += (imageRect.Height - self.icon.Height) // 2
        imageRect.Height = self.icon.Height

        textRect = myBounds.MemberwiseClone()
        textRect.X += self.ICON_SPACE
        textRect.Width -= self.ICON_SPACE
        textRect.Height -= 1
        textRect.Inflate(-1,-1)

        if ((e.State & DrawItemState.Selected) == DrawItemState.Selected):
            self.textBrush.Color = SystemColors.Highlight
            g.FillRectangle(self.textBrush, myBounds)
            self.textBrush.Color = SystemColors.HighlightText
        else:
            self.textBrush.Color = SystemColors.Window
            g.FillRectangle(self.textBrush, myBounds)
            self.textBrush.Color = SystemColors.WindowText

        g.DrawImage(self.icon, imageRect)
        g.DrawString(sender.Items[e.Index], e.Font, self.textBrush,
                     PointF(textRect.X, textRect.Y))

        # Border line (note that Bottom is actually outside our bounds)
        g.DrawLine(Pens.LightGray,
                   Point(e.Bounds.Left,e.Bounds.Bottom-1),
                   Point(e.Bounds.Right,e.Bounds.Bottom-1))

    # ---------------------------------

    def UpdateAllItems(self, contents, keepSelection=False):
        if keepSelection:
            currentSelection = list(self.SelectedIndices)

        # ListBox requires a .NET List; initialise to contain String types.
        formattedItems = List[String]()
        self.DataSource = None

        for moduleName in contents:
            docs = self.moduleManager.GetDocs(moduleName)
            if docs:
                # Issue #20 - only display the base name of the module 
                # in the main UI.
                try:
                    displayName = moduleName.split(".", 1)[1]
                except IndexError:
                    # It is a top-level module with no '<library>.' prefix.
                    displayName = moduleName

                composedString = _("{}, version {}").format(displayName,
                                                            str(docs[FTM_Version]))
                composedString += "\n"
                composedString += docs[FTM_Synopsis]
                
                if docs[FTM_ModifiesDB]:
                    composedString += "\n"
                    # NOTE: Keep the space at the end if your language uses spaces.
                    composedString += _("Note: Can modify the project. ")
                    if not FTConfig.simplifiedRunOps:
                        composedString += _("(Use the 'Run (Modify)' buttons to make changes.)")
                if docs[FTM_HasConfig]:
                    composedString += "\n"
                    composedString += _("Note: This module has configurable parameters.")
            else:
                composedString = "\n"
                composedString += _("Module '{}' is missing or failed to import!").format(moduleName)
                composedString += "\n"
            formattedItems.Add(composedString)
        self.DataSource = formattedItems

        if keepSelection:
            for i in range(len(self.DataSource)):
                self.SetSelected(i, i in currentSelection)

    def SetActivatedHandler(self, handler):
        if handler:
            self.__ActivatedHandler = handler
            # Double-click and Enter will run this module
            if not FTConfig.disableDoubleClick:
                self.DoubleClick += self.__ItemActivatedHandler
            self.KeyDown += self.__ItemActivatedHandler

    def __ItemActivatedHandler(self, sender, event):
        if self.__ActivatedHandler:
            activate = True         # For DoubleClick
            if type(event) == KeyEventArgs:
                activate = (event.KeyCode == Keys.Return)
            if activate:
                self.__ActivatedHandler()
