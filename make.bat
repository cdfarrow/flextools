@ECHO OFF
REM Simple build commands for flextools

set PYTHON=py -3.8

REM Check that the argument is a valid command, and do it. /I ignores case.
FOR %%C IN ("Init"
            "RunTests"
            "Clean"
            "Build"
            "Publish") DO (
            IF /I "%1"=="%%~C" GOTO :Do%1
)
    
:Usage
    echo Usage:
    echo      make init         - Install the libraries that are needed
    echo      make runtests     - Run pytest
    echo      make clean        - Clean out build files
    echo      make build        - Build the project
    echo      make publish      - Publish the project to PyPI
    exit

:DoInit
    %PYTHON% -m pip install -r requirements.txt
    exit
    
:DoRunTests
    %PYTHON% -m pytest
    exit

:DoClean
    rmdir /s /q ".\build"
    rmdir /s /q ".\dist"
    exit
    
:DoBuild
    @REM Build the wheel & the exe with setuptools
    %PYTHON% -m build -w
    exit
    
:DoPublish
    echo Publishing wheel to PyPI
    %PYTHON% -m twine upload .\dist\flextools*
    exit
