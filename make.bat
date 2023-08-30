@ECHO OFF
REM Simple build commands for flextools

REM Build with the default Python version
set PYTHON=py

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
    goto :End

:DoInit
    %PYTHON% -m pip install -r requirements-dev.txt
    goto :End
    
:DoClean
    rmdir /s /q ".\build"
    rmdir /s /q ".\dist"
    goto :End
    
:DoBuild
    @REM Build the wheel for flextoolslibs with setuptools
    %PYTHON% -m build -w
    
    @REM Build the main FlexTools zip file
    %PYTHON% makezip.py
    
    @REM Check for package errors
    %PYTHON% -m twine check .\dist\flextoolslib*
    
    echo The distribution files are in dist\:
    dir dist /b
    goto :End
    
:DoPublish
    echo Publishing wheel to PyPI
    %PYTHON% -m twine upload .\dist\flextoolslib*
    goto :End


:End
