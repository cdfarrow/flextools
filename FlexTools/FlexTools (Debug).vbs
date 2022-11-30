' Run the batch file with VBS script to avoid the black console window.
'
' The '0' parameter to Run hides the console window.

Set WshShell = CreateObject("WScript.Shell")

WshShell.Run "py -3.8 .\scripts\RunFlexTools.py DEBUG", 0, True

WshShell.Run "notepad flextools.log"

WshShell = Null
