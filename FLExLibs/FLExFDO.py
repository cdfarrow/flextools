#
#   FLExFDO.py
#
#   Version-specific code and imports for FieldWorks Language Explorer database access 
#   via FDO (FieldWorks Data Objects) API.
#
#   There have been numerous interface changes over the different
#   FieldWorks versions, so this module handles the differences.
#
#   Platform: Python.NET
#             (ITsString doesn't work in IRONPython)
#             FieldWorks Version 7 & 8
#
#   By: Craig Farrow
#       2008 - 2014
#
#

import os

import clr
clr.AddReference("System")
import System

# Do base configuration and establish FW code path for the following AddReference calls
from FLExBaseInit import FWAppVersion

clr.AddReference("FDO")
clr.AddReference("COMInterfaces")
clr.AddReference("FwUtils")
clr.AddReference("FDOBrowser")
clr.AddReference("FieldWorks")
clr.AddReference("FwCoreDlgs")

# Classes needed for loading the FDO Cache
from SIL.FieldWorks.FDO import FdoCache

if FWAppVersion.CompareTo(System.Version("8.1")) < 0:
    # Less than 8.1
    from SIL.FieldWorks.Common.FwUtils import FwStartupException as StartupException # FW 7.2+
    from SIL.FieldWorks.Common.FwUtils import FDOBackendProviderType # FW 7.1.1+
    from SIL.FieldWorks.Common.FwUtils import DirectoryFinder as FwDirectoryFinder
    # Configure the default directory in ChooseLangProjectDialog()
    FwDirectoryFinder.set_CompanyName("SIL")
else:
    # 8.1 or greater
    from SIL.CoreImpl import StartupException # FW 8.1.0+
    from SIL.FieldWorks.FDO import FDOBackendProviderType # FW 8.1.0+
    from SIL.FieldWorks.Common.FwUtils import FwDirectoryFinder # FW 8.1.0+
    from SIL.FieldWorks.Common.FwUtils import FwUtils 
    from SIL.FieldWorks.FwCoreDlgs import ChooseLangProjectDialog, FwSplashScreen
    clr.AddReference("FdoUi")   # New in 8.1.0
    from SIL.FieldWorks.FdoUi import FwFdoUI
    if FWAppVersion.CompareTo(System.Version("8.2")) >= 0:
        # 8.2 or greater
        from SIL.FieldWorks.Common.COMInterfaces import Icu


from FDOBrowser import BrowserProjectId
from SIL.FieldWorks import ProjectId
from SIL.Utils import ThreadHelper  # IronPython fails on this
from SIL.FieldWorks.Common.Controls import ProgressDialogWithTask

from SIL.CoreImpl import CellarPropertyType


#--- Globals --------------------------------------------------------

# BigStrings were removed in Flex v8
if hasattr(CellarPropertyType, "BigString"):
    CellarStringTypes  = (CellarPropertyType.String,
                          CellarPropertyType.BigString)
    CellarUnicodeTypes = (CellarPropertyType.MultiUnicode,
                          CellarPropertyType.MultiBigUnicode,
                          CellarPropertyType.MultiString,
                          CellarPropertyType.MultiBigString)
else:
    CellarStringTypes  = (CellarPropertyType.String, )
    CellarUnicodeTypes = (CellarPropertyType.MultiUnicode,
                          CellarPropertyType.MultiString)

#-----------------------------------------------------------

def GetListOfDatabases():
    projectsPath = FwDirectoryFinder.ProjectsDirectory
    objs = os.listdir(unicode(projectsPath))
    dbList = []
    for f in objs:
        if os.path.isdir(os.path.join(projectsPath, f)):
            dbList.append(f)
    return sorted(dbList)

#-----------------------------------------------------------

def OpenDatabase(dbName, writeEnabled = False):
    """
    Open the database given by dbName:
        - Either the full path including ".fwdata" suffix, or
        - The name only, opened from the default project location.
        
    writeEnabled : (Awaiting FW support for a read-only mode so that
                    FW doesn't have to be closed for read-only operations.)
    """

    if FWAppVersion.CompareTo(System.Version("8.2")) >= 0:
        Icu.InitIcuDataDir()
    fwDbExt = ".fwdata"
    if os.path.splitext(dbName)[1] == fwDbExt:
        dbFileName = dbName
    else:
        dataPath = FwDirectoryFinder.ProjectsDirectory
        dbFileName = os.path.join(os.path.join(dataPath, dbName),
                                  dbName+fwDbExt)

    # TODO: How to open a project on a server?
    # (See example call to ChooseLangProjectDialog() below)
    projId = BrowserProjectId(FDOBackendProviderType.kXML,
                              dbFileName)

    th = ThreadHelper()

    # FW 8.1.0 changed the interface to CreateCache
    if FWAppVersion.CompareTo(System.Version("8.1")) < 0:
        from System.Windows.Forms import Form
        dlg = ProgressDialogWithTask(Form(), th)

        return FdoCache.CreateCacheFromExistingData(projId,
                                                    "en",
                                                    dlg)

    dlg = ProgressDialogWithTask(th) # Either pass a task or a Form
    ui = FwFdoUI(None, th)           # IHelpTopicProvider, ISynchronizeInvoke 
    dirs = FwDirectoryFinder.FdoDirectories

    if FWAppVersion.CompareTo(System.Version("8.1.2")) < 0:
        # FDO/fdoCache.cs/CreateCacheFromExistingData
        # public static FdoCache CreateCacheFromExistingData(IProjectIdentifier projectId,
        #        string userWsIcuLocale, IFdoUI ui, IFdoDirectories dirs, IThreadedProgress progressDlg)
        return FdoCache.CreateCacheFromExistingData(projId,
                                                    "en",
                                                    ui,
                                                    dirs,
                                                    dlg)
    else:
        # FW 8.1.2 added settings parameter:
        # public static FdoCache CreateCacheFromExistingData(IProjectIdentifier projectId,
        # string userWsIcuLocale, IFdoUI ui, IFdoDirectories dirs, FdoSettings settings, IThreadedProgress progressDlg)
        from SIL.FieldWorks.FDO import FdoSettings
        settings = FdoSettings()

        return FdoCache.CreateCacheFromExistingData(projId,
                                                    "en",
                                                    ui,
                                                    dirs,
                                                    settings,
                                                    dlg)


#----------------------------------------------------------------
##
##from System.Threading import *
##from System.Globalization import CultureInfo
##
####from System.Windows.Forms import Application
##
##def ChooseDatabaseDialog():
##    Thread.CurrentThread.CurrentUICulture = CultureInfo('en') # Override OS default
##    dlg = ChooseLangProjectDialog(None, False) # (helpTopicProvider, openToAssosiateFwProject)
##    dlg.ShowDialog()
##    return dlg.Server, dlg.Project
