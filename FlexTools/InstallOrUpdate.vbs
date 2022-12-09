' Run the FlexTools installer (pip) for first install or to update
' to a later version.

Set WshShell = CreateObject("WScript.Shell")

WshShell.Run "scripts\FlexToolsCommands.vbs INSTALL", 0, True

WshShell = Null
