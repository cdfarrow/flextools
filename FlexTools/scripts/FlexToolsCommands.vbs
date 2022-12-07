'
'   FlexToolsCommands.vbs
'
'   Copyright Craig Farrow, 2022
'
'   A collection of commands for running FlexTools.
'   These are gathered here, so there is only one place to specify
'   which version of Python to use.
'   Additionally, we are using VBS so we can use the '0' parameter to 
'   Run, which hides the console window.
'
'   Usage:
'       FlexToolsCommands.vbs <Command> (<ini-file>)
'
'   The commands are (case insensitive):
'       Run      - run the program
'       Debug    - run FlexTools with debugging output
'       Install  - run pip to install or upgrade flextoolslib
'       List     - output a list of all the FieldWorks projects
'

PY_CMD = "py -3.8"

FT_CMD = PY_CMD&" .\scripts\RunFlexTools.py"


' The ini file name/path can be supplied as an argument.
If WScript.Arguments.Count > 1 Then
    FT_CMD = FT_CMD & " " & WScript.Arguments.Item(1)
End If


Set WshShell = CreateObject("WScript.Shell")

func = GetRef( "Do" & WScript.Arguments.Item(0))

WshShell = Null

'----------------------------------------------------------- 
Function Error()
    MsgBox("Error running FlexTools with command '" & PY_CMD & "'. Please run InstallOrUpdate.vbs, then try again.")
End Function

Function DoRun()
    rc = WshShell.Run(FT_CMD, 0, True)
    If rc <> 0 Then
        Error
    End If
End Function

Function DoDebug()
    rc = WshShell.Run(FT_CMD&" DEBUG", 0, True)
    If rc <> 0 Then
        Error
    Else
        WshShell.Run("notepad flextools.log")
    End If
End Function

Function DoInstall()
    ' Use CMD so we can do a pause to keep the output visible.
    rc = WshShell.Run("%comspec% /c """&PY_CMD&" -m pip install --upgrade flextoolslib & pause""", 1, True)
End Function

Function DoList()
    ' Use CMD so we can do a pause to keep the output visible.
    rc = WshShell.Run("%comspec% /c """&PY_CMD&" .\scripts\ListProjects.py & pause""", 1, True)
End Function
'----------------------------------------------------------- 

