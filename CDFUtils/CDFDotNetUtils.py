#
#   DotNetUtils
#
#
#
#   Craig Farrow
#   June 2010
#

from System.Windows.Forms import (
    MainMenu, MenuItem, Shortcut,
    ToolBar, ToolBarButton, ToolBarButtonStyle, ToolBarAppearance,
    ToolStrip, ToolStripContainer, ToolStripSeparator,
    ImageList,
    DockStyle
    )

from System.Drawing import (Bitmap, Image)
 
# ------------------------------------------------------------------
class CDFMainMenu(MainMenu):
    """
    Creates a .NET MainMenu from an initialised structure:
        List of tuples: (Menu Title, Submenu List)
        Submenu List is a list of tuples:
            (Handler, Text, Shortcut, Tooltip)
            If the Handler is None, then the menu is disabled.
            If the tuple is None, then a separator is inserted.
    """
    def __init__(self, menuList):
        MainMenu.__init__(self)
        for menu in menuList:
            newMenu = MenuItem()
            newMenu.Text, submenuList = menu
            for submenu in submenuList:
                newSubmenu = MenuItem()
                if submenu:
                    handler, newSubmenu.Text, newSubmenu.Shortcut, newSubmenu.Tooltip = submenu
                    if handler:
                        newSubmenu.Click += handler
                    else:
                        newSubmenu.Enabled = False
                else:
                    newSubmenu.Text = "-"       # Separator
                newMenu.MenuItems.Add(newSubmenu)
            self.MenuItems.Add(newMenu)

# ------------------------------------------------------------------
class CDFToolBar(ToolBar):
    """
    Creates a .NET ToolBar from an initialised structure:
        buttonList = List of tuples: 
            (Handler, Text, Image, Tooltip)
            If the Handler is None, then the button is disabled.
            An item of None produces a toolbar separator.
        imagePathTuple = (prefix, suffix) pair to generate a full
            path for loading the images.
    """

    def __init__(self, buttonList, imagePathTuple):
        ToolBar.__init__(self)
        self.Appearance = ToolBarAppearance.Flat
        self.Dock = DockStyle.Top

        self.HandlerList = []
        self.ImageList = ImageList()

        for bParams in buttonList:
            button = ToolBarButton()
            if bParams:
                handler, button.Text, imageName, button.ToolTipText = bParams
                self.ImageList.Images.Add(
                    Bitmap.FromFile(imageName.join(imagePathTuple)))
                button.ImageIndex = self.ImageList.Images.Count-1
                
                self.HandlerList.append(handler)
                button.Tag = len(self.HandlerList)-1 
            else:
                button.Style = ToolBarButtonStyle.Separator
            self.Buttons.Add(button)

        self.ButtonClick += self.__OnButtonClick

    def __OnButtonClick(self, sender, event):
        if event.Button.Tag is not None:               # zero is a valid value
            if self.HandlerList[event.Button.Tag]:
                self.HandlerList[event.Button.Tag]()   # The event handler
                
    def UpdateButtonText(self, buttonIndex, newText):
        self.Buttons[buttonIndex].Text = newText
