#
#   FLExBaseInit.py
#
#   Module: Fieldworks Language Explorer registry information
#           and other system configuration.
#
#   Note:   This module needs to be imported before importing or
#           using any Fieldworks Assemblies as it sets up the
#           path, and other low-level things.
#
#   Platform: Python.NET & IRONPython
#
#   By: Craig Farrow
#       2011 - 2014
#

import sys
import os
import glob
import shutil

import clr
import System
clr.AddReference("System.Data")

import System.Xml
clr.AddReference("System.Xml")
from System.Xml import XmlDocument


#----------------------------------------------------------------

clr.AddReference("mscorlib")        # Where Win32 assembly resides
from Microsoft.Win32 import Registry, RegistryKey

#----------------------------------------------------------------
# Fieldworks registry constants

FWRegKeys = { "7" : r"SOFTWARE\SIL\Fieldworks\7.0",
              "8" : r"SOFTWARE\SIL\Fieldworks\8" }

FWRegCodeDir = "RootCodeDir"
FWRegProjectsDir = "ProjectsDir"

#----------------------------------------------------------------
def GetFWRegKey(fwVersion):

    try:
        RegKey = FWRegKeys[fwVersion]
    except KeyError:
        raise Exception("Error: Unsupported Fieldworks version (%s)" % fwVersion)

    rKey = Registry.CurrentUser.OpenSubKey(RegKey)
    if rKey and rKey.GetValue(FWRegCodeDir):
        return rKey
    rKey = Registry.LocalMachine.OpenSubKey(RegKey)
    if rKey and rKey.GetValue(FWRegCodeDir):
        return rKey

    return None


def InitialiseFWGlobals():
    global FWCodeDir
    global FWProjectsDir
    global FWMajorVersion

    # The environment variable FWVersion is configured by py_net.bat to tell us
    # which version of the FW DLLs we are running with (so we know which path
    # to use for FW libraries.)
    try:
        FWMajorVersion = os.environ["FWVersion"]
    except KeyError:
        raise Exception("Error: FWVersion environment variable not defined!")

    print "Startup: py_net.bat set FwVersion =", FWMajorVersion
    rKey = GetFWRegKey(FWMajorVersion)
    if not rKey:
        raise Exception("Can't find Fieldworks %s!" % FWMajorVersion)

    codeDir = rKey.GetValue(FWRegCodeDir)
    projectsDir = rKey.GetValue(FWRegProjectsDir)

    print "Startup: Reg codeDir =", codeDir
    print "Startup: Reg projectsDir =", projectsDir

    # On developer's machines we also check the build directories for FieldWorks.exe

    if not os.access(os.path.join(codeDir, "FieldWorks.exe"), os.F_OK):
        if os.access(os.path.join(codeDir, r"..\Output\Release\FieldWorks.exe"), os.F_OK):
            codeDir = os.path.join(codeDir, r"..\Output\Release")
        elif os.access(os.path.join(codeDir, r"..\Output\Debug\FieldWorks.exe"), os.F_OK):
            codeDir = os.path.join(codeDir, r"..\Output\Debug")
        else:
            raise Exception("Error: Can't find path for FieldWorks.exe.")
        
    FWCodeDir = codeDir
    FWProjectsDir = projectsDir

    print "Startup: FWCodeDir =", FWCodeDir
    print "Startup: FWProjectsDir =", FWProjectsDir

# Initialise globals for which version of FW we are using.
InitialiseFWGlobals()

#----------------------------------------------------------------
# Add the FW code directory to the search path for importing FW libs.
sys.path.append(FWCodeDir)

#----------------------------------------------------------------
# The following imports rely on the FW Code path appended above:

if FWMajorVersion == "8":
    # Get the full version information out of FW itself
    clr.AddReference("CoreImpl")
    from SIL.CoreImpl import VersionInfoProvider
    from System.Reflection import Assembly

    vip = VersionInfoProvider(Assembly.GetAssembly(VersionInfoProvider), False)
    FWAppVersion = System.Version(vip.ShortNumericAppVersion) # e.g. 8.1.3
else:
    # Get the full version information out of FW itself
    clr.AddReference("FwUtils")
    from SIL.FieldWorks.Common.FwUtils import FwVersionInfoProvider
    from System.Reflection import Assembly

    vip = FwVersionInfoProvider(Assembly.GetAssembly(FwVersionInfoProvider), False)
    i = vip.ApplicationVersion.find(": ")
    FWAppVersion = System.Version(vip.ApplicationVersion[i+2:i+7]) # e.g. 7.2.4

FWFullVersion = vip.ApplicationVersion
print "Startup: FW Version =", FWFullVersion

clr.AddReference("SILUtils")
from SIL.Utils import RegistryHelper
clr.AddReference("FwCoreDlgs")
from SIL.FieldWorks.Common.FwUtils import FwRegistryHelper

# Module initialisation - tell the system which application we are.
# (Note that Python doesn't find the set method with .ProductName, possibly
#  because the get method is private.)

# Configure ICU code to find it's data (in CreateCacheFromExistingData())
RegistryHelper.set_CompanyName("SIL")
RegistryHelper.set_ProductName("FieldWorks")


#----------------------------------------------------------------

def CopyIfDifferent(source, target):
    """
    Copy a file from one path to another if the target doesn't exist, or
    if the source has changed.
    Raises SystemError if there is a failure to copy.
    Ignores a missing source file.
    Returns True if the file was updated.
    """
    
    def FilesEqual(firstFileName, secondFileName, blocksize=65536):
        if os.path.getsize(firstFileName) != os.path.getsize(secondFileName):
            return False

        firstFile  = open(firstFileName,  'rb')
        secondFile = open(secondFileName, 'rb')

        result = True
        buf1 = firstFile.read(blocksize)
        buf2 = secondFile.read(blocksize)
        while len(buf1) > 0:
            if buf1!=buf2:
                result = False
                break
            buf1, buf2 = firstFile.read(blocksize), secondFile.read(blocksize)
        firstFile.close()
        secondFile.close()
        return result
    
    copy = False
    if os.access(source, os.F_OK):
        if not os.access(target, os.F_OK):
            copy = True
        elif not FilesEqual(source, target):
            copy = True
        if copy:
            try:
                # copyfile doesn't copy RO mode so we can overwrite next time
                shutil.copyfile(source, target)
            except IOError:
                raise SystemError("Error copying %s to %s! Check write permissions." %\
                        (source, target))
    return copy
    

def FWConfigureDLLs():
    """
    Copies FW COM DLLs to Python.NET directories.
    Ensures we are using the right python32.exe.manifest file.
    """

    # The Fieldworks COM DLLs (FwKernel.dll and Language.dll) need to be
    # specially handled for FDO code to work. There are two options:
    #  - either register them (with 'regsvr32 <dll>')
    #  - or have them in the same directory as python.exe, and use a
    #    manifest file with python.exe.
    # Feb2012 I tried the former, but at least one user had problems
    # registering language.dll on a 64 bit OS, so I'm trying the latter now.
    #
    # Copy the DLLs into the PythonXX.NET directories if they aren't there.
    #  - DebugProcs.dll is for developers' machines.
    #  - icuuc50.dll is also needed; icuuc54.dll for Flex 8.2.2+
    #  - Language.dll was removed in FW 8.1.0, still copy for earlier versions.

    py_net_folders = glob.glob("..\Python*.NET\FW%s" % FWMajorVersion)
    FWFiles = ["Language.dll", "Fwkernel.dll", "FwKernel.X.manifest",
               "icuuc50.dll", "icuuc54.dll", "icuin54.dll",
               "DebugProcs.dll"]
    
    for folder in py_net_folders:
        for fwFile in FWFiles:
            sourcename = os.path.join(FWCodeDir, fwFile)
            targetname = os.path.join(folder, fwFile)
            if CopyIfDifferent(sourcename, targetname): # Ignores missing files
                print "Startup: Copied", sourcename, "to", targetname

Python32Manifest = \
"""<?xml version="1.0" encoding="utf-8"?>
<assembly manifestVersion="1.0" xmlns:asmv1="urn:schemas-microsoft-com:asm.v1" xmlns:asmv2="urn:schemas-microsoft-com:asm.v2" xmlns:dsig="http://www.w3.org/2000/09/xmldsig#" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="urn:schemas-microsoft-com:asm.v1 assembly.adaptive.xsd" xmlns="urn:schemas-microsoft-com:asm.v1">
    <assemblyIdentity name="nPython.exe" version="2.0.0.4" type="win32" />
    <dependency>
        <dependentAssembly asmv2:codebase="FwKernel.X.manifest">
            <assemblyIdentity name="FwKernel.X" version="8.1.2.0" type="win32" />
        </dependentAssembly>
    </dependency>
</assembly>
"""


def FWConfigureManifest():
    """
    Configures python manifest file according to the current version of 
    FieldWorks.
    Returns True if FlexTools needs to be restarted (necessary if
    the manifest file has been changed)
    """
    # Nov2014:
    # There are different versions of python32.exe.manifest for different versions of FieldWorks
    # FW 7: this one is stable and distributed in the PythonXX.NET\FW7 directories
    # FW 8.0: distributed in the PythonXX.NET\FW8 directories
    # FW 8.1: reference FwKernel.X.manifest from a created python32.exe.manifest
    #         so we can pick up updates automatically.

    restartRequired = False

    FwKernelManifestName = "FwKernel.X.manifest"
    Python32ManifestName = "python32.exe.manifest"
    # For FW 8.1+
    FwKernelManifestPath = os.path.join(FWCodeDir, FwKernelManifestName)
    if os.access(FwKernelManifestPath, os.F_OK):        # Doesn't exist in FW 7
        # FwKernel.X.manifest will have been copied by FWConfigureDLLs()

        # Find version number of FwKernel.X.manifest
        FwKernelXML = XmlDocument()
        FwKernelXML.Load(FwKernelManifestPath)

        # <assemblyIdentity name="FwKernel.X" version="8.1.2.41947" type="win32" />
        FwKernelVersion = FwKernelXML.DocumentElement.FirstChild.GetAttribute("version")

        Python32ManifestXML = XmlDocument()
        Python32ManifestXML.LoadXml(Python32Manifest)

        Python32ManifestXML.DocumentElement.LastChild.FirstChild.FirstChild.SetAttribute("version", FwKernelVersion)
        # print Python32ManifestXML.DocumentElement.LastChild.FirstChild.FirstChild.GetAttribute("version")

        py_net_folders = glob.glob("..\Python*.NET\FW%s" % FWMajorVersion)

        # Compare with version number in each python32.exe.manifest
        for folder in py_net_folders:
            manifestFilename = os.path.join(folder, Python32ManifestName)
            ToCheckXML = XmlDocument()
            ToCheckXML.Load(manifestFilename)

            try:
                ver = ToCheckXML.DocumentElement.LastChild.FirstChild.FirstChild.GetAttribute("version")
            except AttributeError:
                # Arrives here with the default python32.exe.manifest for earlier versions of FW.
                ver = ""

            # If different then write a new python32.exe.manifest, and force restart
            if ver <> FwKernelVersion:
                restartRequired = True
                Python32ManifestXML.Save(manifestFilename)  # Overwrite the manifest
                print "Startup: Manifest updated:", manifestFilename

    return restartRequired

#----------------------------------------------------------------

# Configure the path to find the library modules.
import site
site.addsitedir("../")

print "SYS.PATH:"
for x in sys.path: print x

from CDFConfigStore import CDFConfigStore

FWVERSIONFILE = "__FWVersion.ini"
FWVersionStore = CDFConfigStore(FWVERSIONFILE)

if FWVersionStore.Version <> FWFullVersion:
    print "Startup: Saved FW Version updated -", FWVersionStore.Version, "-->", FWFullVersion
    FWVersionStore.Version = FWFullVersion
    
    # Configure Fieldworks DLLs and manifest since the FW version has changed.
    FWConfigureDLLs()
    restartRequired = FWConfigureManifest()
    
    # Save the file before restart (but after the call to FWConfigureManifest()
    # in case something fails in there.)
    del FWVersionStore          
    
    if restartRequired:
        print "Startup: Restart required."
        print
        raise EnvironmentError("FLExTools has updated its configuration to match the new version of Fieldworks. Restarting.")
        
