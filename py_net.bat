@echo OFF
REM	We need to run Python as a 32 bit application, which requires
REM	that we launch it from a 32 bit command prompt on 64 bit windows.
REM	We use the ProgramFiles environment variables to detect whether
REM	we are running the 32 bit or 64 bit cmd.exe and relaunch this
REM	batch file with the 32 bit version if required.

REM	On 64 bit Windows with 64 bit command prompt:
REM		ProgramFiles=C:\Program Files
REM		ProgramFiles(x86)=C:\Program Files (x86) 
REM	On 64 bit Windows with 32 bit command prompt:
REM		ProgramFiles=C:\Program Files (x86)
REM		ProgramFiles(x86)=C:\Program Files (x86) 

if not defined ProgramFiles(x86) goto Run32Bit

REM echo 64 bit Windows detected

if "%ProgramFiles(x86)%" == "%ProgramFiles%" goto Run32Bit

REM echo Running 64 bit cmd.exe (launching 32 bit cmd.exe...)

REM echo Calling %0 %*
%SystemRoot%\SysWow64\cmd.exe /c %0 %*

REM echo Leaving 64 bit cmd.exe
exit /b

:----------------------------------------------------------
:Run32Bit

REM echo Running 32 bit cmd.exe

REM Detect which version of Fieldworks is installed

reg query "hklm\Software\SIL\Fieldworks\8" >nul 2>nul
if errorlevel 1 reg query "hkcu\Software\SIL\Fieldworks\8" >nul 2>nul
if errorlevel 1 goto checkFW7

set FWVersion=8
goto GotFWVersion

:checkFW7
reg query "hklm\Software\SIL\Fieldworks\7.0" >nul 2>nul
if errorlevel 1 reg query "hkcu\Software\SIL\Fieldworks\7.0" >nul 2>nul
if errorlevel 1 goto FWNotFound

set FWVersion=7

:----------------------------------------------------------
:GotFWVersion

REM Find the latest version of Python that is installed out of 2.5, 2.6 and 2.7

reg query "hklm\Software\Python\PythonCore\2.7" >nul 2>nul
if errorlevel 1 reg query "hkcu\Software\Python\PythonCore\2.7" >nul 2>nul
if errorlevel 1 goto check26

REM Set PYTHONHOME to Python installation
for /f "tokens=3" %%a in ('reg query "hklm\Software\Python\PythonCore\2.7\InstallPath" ^| find "REG_SZ"') do set PYTHONHOME=%%a

call ..\Python27.NET\FW%FWVersion%\python32.exe  %*
goto END

:check26
reg query "hklm\Software\Python\PythonCore\2.6" >nul 2>nul
if errorlevel 1 reg query "hkcu\Software\Python\PythonCore\2.6" >nul 2>nul
if errorlevel 1 goto check25

call ..\Python26.NET\FW%FWVersion%\python32.exe  %*
goto END

:check25
reg query "hklm\Software\Python\PythonCore\2.5" >nul 2>nul
if errorlevel 1 reg query "hkcu\Software\Python\PythonCore\2.5" >nul 2>nul
if errorlevel 1 goto PythonNotFound

call ..\Python25.NET\FW%FWVersion%\python32.exe  %*
goto END

:PythonNotFound
REM echo Can't find 32-bit Python 2.5, 2.6 or 2.7!

echo MsgBox "Can't find 32-bit Python 2.5, 2.6 or 2.7!",0,"FLExTools" >%temp%\FTMsg.vbs
call %temp%\FTMsg.vbs
del %temp%\FTMsg.vbs

goto END

:FWNotFound
echo MsgBox "Can't find Fieldworks 7 or 8.",0,"FLExTools" >%temp%\FTMsg.vbs
call %temp%\FTMsg.vbs
del %temp%\FTMsg.vbs

goto END


:END
REM Errorlevel 2 signals a restart is required (DLLs or manifests updated)
if errorlevel 2 goto GotFWVersion
