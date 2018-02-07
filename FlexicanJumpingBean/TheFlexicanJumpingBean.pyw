# The FLExican Jumping Bean
#
# Craig Farrow
# 7 Feb 2008
#
# See instructions below.

import wx
import wx.html
import os

# Populate this list with FLEx links (or to other software that supports
# hyperlinks like this.)
# This is a list of tuples in the form (description, link)

flexLinks = [
     ("'Good' in wordforms", "silfw://localhost/link?app%3dLanguage+Explorer%26tool%3dAnalyses%26guid%3d5b874465-ae5e-46ac-b739-c3bddd6cacfa%26server%3d.%5cSILFW%26database%3dMyDB")
    ,("Ad hoc grammar rules", "silfw://localhost/link?app%3dLanguage+Explorer%26tool%3dAdhocCoprohibEdit%26guid%3dnull%26server%3d.%5cSILFW%26database%3dMyDB")
    ,("'Good' in Lexicon", "silfw://localhost/link?app%3dLanguage+Explorer%26tool%3dlexiconEdit%26guid%3d54c9ff04-5d72-44e8-a37e-01a3feb3d453%26server%3d.%5cSILFW%26database%3dMyDB")
             ]

htmlDescription = """
<h3>The FLExican Jumping Bean</h3>
<p>This little utility makes use of SIL FieldWorks Language Explorer (FLEx)'s
hyperlink capability to navigate
within FLEx by clicking on the icon in the taskbar.</p>

<p>This could be used, for example, when giving a demonstration of
FLEx.
You can set up the things in FLEx that you want to show in this program,
and then just click your way through. FLEx is not in any way disabled so you
can still do normal operations there as part of the demo.</p>

<p>To set it up, go to each place in FLEx that you want to jump to and
select the menu item Edit | Copy Location as Hyperlink.
Then in this Python file
paste the Hyperlink into the list "flexLinks". Add a comment describing the
link. When you are done just run the program and click on the taskbar icon
to activate the Hyperlinks one at a time. The tool-tip on the icon shows
what is coming next; and in the right-click menu you can reset
to the start of the list.</p>

<p>Close this window or use the taskbar icon's menu to exit.</p>

<p><b>Have fun!</b></p>

"""


class HTMLDescription(wx.html.HtmlWindow):
    def __init__(self, parent):
        wx.html.HtmlWindow.__init__(self, parent, -1,
                                    style=wx.NO_FULL_REPAINT_ON_RESIZE)
        
        self.SetPage( htmlDescription )
        
class Frame(wx.Frame):
    def __init__(
            self, parent, pos=wx.DefaultPosition, size=(450,450),
            style=wx.DEFAULT_FRAME_STYLE 
        ):
        wx.Frame.__init__(self, parent, -1,
                          "The FLExican Jumping Bean",
                          pos, size, style)

        description = HTMLDescription(self)
        
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)

        # Load the icon
        icon = wx.Icon("JumpingBean.ico", wx.BITMAP_TYPE_ICO )
        self.SetIcon(icon)
        
        try:
            self.tbicon = BeanIcon(self, icon)
        except:
            self.tbicon = None
        self.Show(False)
 
    def OnCloseWindow(self, event):
        if self.tbicon is not None:
            self.tbicon.Destroy()
        self.Destroy()

        
# All the work happens in here.
# A Taskbar icon:
#   - Click on the icon to jump to the next link
#   - Menu | Reset starts over at the first link.
#   - Menu | Close closes the program.
class BeanIcon(wx.TaskBarIcon):
    TBMENU_CLOSE   = wx.NewId()
    TBMENU_RESET   = wx.NewId()

    def _MakeToolTip(self):
        if self.jumpIndex < len(flexLinks):
            return str(self.jumpIndex) + ": " + flexLinks[self.jumpIndex][0]
        else:
            return "End of list - select Reset to start again"
                            
    def __init__(self, frame, icon):
        wx.TaskBarIcon.__init__(self)
        self.frame = frame
        self.icon = icon

        self.jumpIndex = 0
        
        self.SetIcon(self.icon, self._MakeToolTip())

        # bind some events
        self.Bind(wx.EVT_TASKBAR_LEFT_DOWN, self.OnTaskBarClick)
        self.Bind(wx.EVT_MENU, self.OnTaskBarClose, id=self.TBMENU_CLOSE)
        self.Bind(wx.EVT_MENU, self.OnTaskBarReset, id=self.TBMENU_RESET)

    def CreatePopupMenu(self):
        """
        Create our menu. 
        """
        menu = wx.Menu()
        menu.Append(self.TBMENU_CLOSE,   "Close")
        menu.AppendSeparator()
        menu.Append(self.TBMENU_RESET, "Reset")
        return menu

    def OnTaskBarClick(self, evt):
        if self.jumpIndex < len(flexLinks):
            os.startfile(flexLinks[self.jumpIndex][1])      # Jump!
            self.jumpIndex += 1
            self.SetIcon(self.icon, self._MakeToolTip())    # Update the tooltip

    def OnTaskBarReset(self, evt):
        self.jumpIndex = 0
        self.SetIcon(self.icon, self._MakeToolTip())

    def OnTaskBarClose(self, evt):
        self.frame.Close()

   

class MyApp(wx.App):
    def OnInit(self):
        frame = Frame(None)
        self.SetTopWindow(frame)
        frame.Show()
        return True


if __name__ == '__main__':
    app = MyApp(0)
    app.MainLoop()
    app.Destroy()



