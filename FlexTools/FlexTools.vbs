' Run the batch file with VBS script to avoid the black console window.
'
' The '0' parameter to Run hides the console window.

Set WshShell = CreateObject("WScript.Shell")

WshShell.Run "FlexTools.bat", 0, True

WshShell = Null
