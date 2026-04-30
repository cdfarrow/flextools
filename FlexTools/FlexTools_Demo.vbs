' Run FlexTools in demonstration mode (larger fonts and windows)

Set WshShell = CreateObject("WScript.Shell")

WshShell.Run "scripts\FlexToolsCommands.vbs DEMO", 0, True

WshShell = Null
