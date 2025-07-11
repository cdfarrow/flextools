@ECHO OFF
REM Simple build commands for flextools

REM Build with the default Python version
set PYTHON=py

REM Check that the argument is a valid command, and do it. /I ignores case.
FOR %%C IN ("Init"
            "Clean"
            "Extract"
            "Compile"
            "Build"
            "Publish") DO (
            IF /I "%1"=="%%~C" GOTO :Do%1
)
    
:Usage
    echo Usage:
    echo      make init         - Install the libraries for building
    echo      make clean        - Clean out build files
    echo      make extract      - Update the translation strings template
    echo      make compile      - Update the translation files
    echo      make build        - Build the project
    echo      make publish      - Publish the project to PyPI
    goto :End

:DoInit
    %PYTHON% -m pip install -r requirements-dev.txt
    goto :End
    
:DoClean
    del /s *.mo
    rmdir /s /q ".\build"
    rmdir /s /q ".\dist"
    goto :End
    
:DoExtract
    @REM Build the translation files:
    pushd flextoolslib\locales\
    @REM  - Create the template from the source code
    pybabel extract ..\code -o body.pot --omit-header --no-wrap -c NOTE:
    @REM  - Join it with the pre-populated header. (Binary to keep the Unix EOLs.)
    cmd /c copy /b header.pot+body.pot flextools.pot
    popd
    goto :END
    
:DoCompile
    @REM  - Compile the .mo files
    pybabel compile -D flextools -d flextoolslib\locales\ --statistics   
    goto :END
    
:DoBuild
    @REM  - Compile the .mo files
    pybabel compile -D flextools -d flextoolslib\locales\

    @REM Build the wheel for flextoolslib with setuptools
    %PYTHON% -m build -w
    
    @REM Build the main FlexTools zip file
    %PYTHON% makezip.py
    
    @REM Check for package errors
    %PYTHON% -m twine check .\dist\flextoolslib*
    
    echo The distribution files are in dist\:
    dir dist /b
    goto :End
    
:DoPublish
    echo Publishing flextoolslib to PyPI
    %PYTHON% -m twine upload .\dist\flextoolslib*
    goto :End


:End
