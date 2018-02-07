' Run the batch file with VBS script to avoid the black console window.
'
' The '0' parameter to Run hides the console window, however it also
' causes FlexTools to appear behind other active windows. The sleep
' and AppActivate bring it to the front.

Set WshShell = CreateObject("WScript.Shell")

WshShell.CurrentDirectory = "FlexTools"

WshShell.Run "..\py_net.bat FLExTools.py >..\error.log", 0

WScript.Sleep (1000)			'Give time for FlexTools to start
WshShell.AppActivate("FlexTools ")	'Bring to front

WshShell = Null
