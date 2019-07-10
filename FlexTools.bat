@echo off

pushd FlexTools

REM Assume that the default Python will match FLEx for 32/64 bit.
REM If it doesn't, then the user will need to install the correct Python.

REM Try py -2 to run Python 2.7
py -2 FlexTools.py >..\error.log %* && goto END

REM If that failed, try "python"
python FlexTools.py >..\error.log %* && goto END

:END
popd
REM notepad error.log
