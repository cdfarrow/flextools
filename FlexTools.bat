@echo off

REM Assume that the default Python will match FLEx for 32/64 bit.
REM If it doesn't, or it is an unsupported Python version, then 
REM add a parameter to the command below to select the right version.
REM Use "py --help" to see the options.

py FlexTools\FlexTools.py %*

:END
