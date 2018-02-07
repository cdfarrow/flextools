These files are built from source with the PYTHON26 conditional compilation
symbol set. The source code can be found at: http://sourceforge.net/projects/pythonnet/.

Fieldworks 8 targets .NET 4, and Python.NET is built from the latest revision "r159" 
Fieldworks 7 targets .NET 3.5 and Python.NET is built from an older revision.

Jan2014: A bug fix has been applied to the FW8 build for an API update in Windows 8.1
	 (See http://sourceforge.net/p/pythonnet/bugs/23/)

Python32.exe is built from source with these changes (by Damien D using full Visual Studio):
	- x86 (i.e. 32 bit) so that it will run in 32 bit mode on 64 bit systems;
	- No embedded manifest--using an external manifest so it is easier to update
	  if we ever need to.

Python32.exe.manifest:
	- References FieldWorks FwKernel.dll and Language.dll.
	  If those DLLs change then a new manifest could be created based on FieldWorks 
	  FDOBrowser.exe.manifest with the application name and version changed to 
	  nPython.exe and 2.0.0.4

