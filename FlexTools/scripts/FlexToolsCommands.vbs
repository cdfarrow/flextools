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
'       Run      - run FlexTools
'       Debug    - run FlexTools with debugging output
'       Install  - run pip to install or upgrade flextoolslib
'       List     - output a list of all the FieldWorks projects
'

Set WshShell = CreateObject("WScript.Shell")
Set FSO = CreateObject("Scripting.FileSystemObject")
ScriptsDir = FSO.GetParentFolderName(WScript.ScriptFullName)

Q = """"

PYTHON = "py"

FLEXTOOLS = PYTHON & " " & Q & FSO.BuildPath(ScriptsDir, "RunFlexTools.py") & Q


' The ini file name/path can be supplied as the first argument.
If WScript.Arguments.Count > 1 Then
    FLEXTOOLS = FLEXTOOLS & " " & WScript.Arguments.Item(1)
End If

' Jump table: call the function matching the command
func = GetRef("Do" & WScript.Arguments.Item(0))

WshShell = Null

'----------------------------------------------------------- 
Function ErrorMsg()
    MsgBox("Error running FlexTools with command '" & PYTHON & "'. Please run InstallOrUpdate.vbs, then try again.")
End Function

Function DoRun()
    rc = WshShell.Run(FLEXTOOLS, 0, True)
    If rc <> 0 Then ErrorMsg
End Function

Function DoDebug()
    If FSO.FileExists("flextools.log") Then
        FSO.DeleteFile("flextools.log")
    End If
    rc = WshShell.Run(FLEXTOOLS & " DEBUG", 0, True)
    If rc <> 0 Then ErrorMsg
    If FSO.FileExists("flextools.log") Then
        WshShell.Run("notepad flextools.log")
    End If
End Function

Function DoInstall()
    ' Use CMD so we can do a pause to keep the output visible.
    rc = WshShell.Run("%comspec%  /c """&PYTHON&" -m pip install --upgrade -r scripts\requirements.txt & pause""", 1, True)
End Function

Function DoList()
    ' Use CMD so we can do a pause to keep the output visible.
    rc = WshShell.Run("%comspec% /c """&PYTHON&" .\scripts\ListProjects.py & pause""", 1, True)
End Function
'----------------------------------------------------------- 

