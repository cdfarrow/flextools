' Run FlexTools with debug logging enabled

Set WshShell = CreateObject("WScript.Shell")

WshShell.Run "scripts\FlexToolsCommands.vbs DEBUG", 0, True

WshShell = Null
