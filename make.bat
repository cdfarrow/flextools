@ECHO OFF
REM Simple build commands for flextools

set PYTHON=py -3.8

REM Check that the argument is a valid command, and do it. /I ignores case.
FOR %%C IN ("Init"
            "Clean"
            "Build"
            "Publish") DO (
            IF /I "%1"=="%%~C" GOTO :Do%1
)
    
:Usage
    echo Usage:
    echo      make init         - Install the libraries for building
    echo      make clean        - Clean out build files
    echo      make build        - Build the project
    echo      make publish      - Publish the project to PyPI
    exit

:DoInit
    %PYTHON% -m pip install -r requirements.txt
    exit
    
:DoClean
    rmdir /s /q ".\build"
    rmdir /s /q ".\dist"
    exit
    
:DoBuild
    @REM Build the wheel for flextoolslibs with setuptools
    %PYTHON% -m build -w -n
    @REM Build the main FlexTools zip file
    %PYTHON% makezip.py
    exit
    
:DoPublish
    echo Publishing wheel to PyPI
    %PYTHON% -m twine upload .\dist\flextools*
    exit
