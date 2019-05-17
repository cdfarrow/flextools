@echo off

pushd FlexTools

REM Try py -2 to run Python 2.7
py -2 FlexTools.py >..\error.log %* && goto END

REM If that failed, try "python"
python FlexTools.py >..\error.log %* && goto END

:END
popd
REM notepad error.log
