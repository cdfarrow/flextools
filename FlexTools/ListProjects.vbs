' Run the FlexTools application

Set WshShell = CreateObject("WScript.Shell")

WshShell.Run "scripts\FlexToolsCommands.vbs LIST", 0, True

WshShell = Null
