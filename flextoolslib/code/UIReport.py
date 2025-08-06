#
#   Project: FlexTools
#   Module:  UIReportWindow
#   Platform: .NET v2 Windows.Forms (Python.NET 2.5)
#
#   A custom list for status report messages from a FlexTools Module.
#
#   Craig Farrow
#   September 2010
#

import os

import logging
logger = logging.getLogger(__name__)

from . import UIGlobal
from . import FTReport

from System.Drawing import (
    Bitmap,
    )

from System.Windows.Forms import (
    Application,
    DockStyle, View,
    ListView, ListViewItem, ColumnHeaderStyle,
    HorizontalAlignment, 
    ImageList, ColorDepth,
    Clipboard,
    )

from System import Environment

# ------------------------------------------------------------------

class ReportWindow(ListView):
    def __init__(self):
        ListView.__init__(self)
        self.SuspendLayout()

        # List appearance
        self.Dock = DockStyle.Fill
        self.View = View.Details
        self.GridLines = True
        self.FullRowSelect = True
        self.HeaderStyle = getattr(ColumnHeaderStyle, "None")
        self.ShowItemToolTips = True
        self.Columns.Add("", -2, HorizontalAlignment.Left)

        # Events
        self.Resize += self.__OnResize
        self.DoubleClick += self.__OnDoubleClick

        # Register this class as the sink for all messages.
        # The higher level passes self.Reporter to the Modules.
        self.Reporter = FTReport.FTReporter()
        self.Reporter.RegisterUIHandler(self.Report)

        # Configure icons
        self.SmallImageList = ImageList()
        self.SmallImageList.ColorDepth = ColorDepth.Depth32Bit
        images = ("information", "exclamation", "cross_circle")
        path, suffix = UIGlobal.ReportIconParams
        for i in images:
            self.SmallImageList.Images.Add(
                Bitmap.FromFile(os.path.join(path, i+suffix)))
        self.ResumeLayout(False)

    def __OnResize(self, sender, event):
        # Allow for scroll bar plus extra to stop horizontal scroll bar appearing.
        self.Columns[0].Width = self.Size.Width - 24

    def __OnDoubleClick(self, sender, event):
        if sender.SelectedItems.Count:
            item = sender.SelectedItems[0]
            if item.Tag and item.Tag.startswith(("silfw:", "file:")):
                try:
                    os.startfile(item.Tag)
                except FileNotFoundError as e:
                    logger.error(f"os.startfile failed with {item.Tag}")

    def Report(self, reportItem):
        if type(reportItem) == tuple:
            msgType, msg, extra = reportItem
            if msg == None: msg = ""            # If None then no icon shows
            item = ListViewItem([msg], msgType) # 2nd = image index; 3 => no icon
            if extra:
                try:
                    if extra.startswith("silfw:"):
                        item.ToolTipText = _("Double-click to jump to Fieldworks")
                    elif extra.startswith("file:"):
                        item.ToolTipText = _("Double-click to open file")
                    else:
                        item.ToolTipText = extra
                    item.Tag = extra
                except AttributeError:      # Not a string
                    item.Tag = item.ToolTipText = repr(extra)
            addedItem = self.Items.Add(item)
        else:
            addedItem = self.Items.Add(reportItem)
        addedItem.EnsureVisible()
        if self.Items.Count % 10 == 0:
            Application.DoEvents()

    def CopyToClipboard(self):
        def __getData(item):
            if item.Tag:
                if item.Tag.startswith("silfw:"):
                    return item.Text
                else:
                    return Environment.NewLine.join((item.Text, 
                                                     item.ToolTipText))
            else:
                return item.Text

        data = [__getData(i) for i in self.Items]

        if data:
            Clipboard.SetText(Environment.NewLine.join(data))
        else:
            Clipboard.Clear()

    def Clear(self):
        self.Reporter.Reset()
        self.Items.Clear()
