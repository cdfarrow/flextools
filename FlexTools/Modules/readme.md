Modules Folder
==============

This folder contains FlexTools modules that are supplied with FLExTools.
New modules (.py files) can be added to this folder or sub-folders.

It is suggested that organisations/entities or individual authors create 
a subdirectory for their modules. These can be distributed as a zipped 
folder and simply unzipped into the Modules directory by end-users.

A FLExTools module must include the following:

Imports
-------

```python
from FTModuleClass import *

#(These are needed for string operations)
from SIL.LCModel.Core.KernelInterfaces import ITsString, ITsStrBldr
from SIL.LCModel.Core.Text import TsStringUtils 
```

Define a 'docs' dictionary
--------------------------

```python
docs = {FTM_Name       : "<name of module>",
        FTM_Version    : "1.0",
        FTM_ModifiesDB : True/False,
        FTM_Synopsis   : "<description of module>",
        FTM_Help       : None/link-to-help-file[pdf,html,etc.],
        FTM_Description: 
"""
<a multi-line full description of the module and how to use it>
"""
}
```

Define a main function and 'FlexToolsModule'
--------------------------------------------

```python
def Main(flexProject, report, modifyAllowed):
    report.Info("Processing...")
    pass

FlexToolsModule = FlexToolsModuleClass(runFunction = Main,
                                       docs = docs)
```

Path Matters
============

If python library files are included with the FLExTools modules (to be imported by the main module), then they can be put in a Libs sub-folder and a !=.pth file added here, which references that folder. See chinese.pth for an example.

