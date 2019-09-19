@echo off

REM Assume that the default Python will match FLEx for 32/64 bit.
REM If it doesn't, then the user needs to install the correct Python
REM or call FLExTools.py manually with the correct Python.exe.

python FlexTools\FlexTools.py %*

:END
