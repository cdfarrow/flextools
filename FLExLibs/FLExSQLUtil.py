#
#   FLExSQLUtil.py
#
#   Module: Fieldworks Language Explorer low-level database access
#           functions via SQL.
#
#
#   Platform: Python.NET & IRONPython
#             Fieldworks v6
#
#   By: Craig Farrow
#       Feb 2009
#

import System
import clr
clr.AddReference("System.Data")

from System.Data.SqlClient import SqlConnection, SqlCommand
from System import Environment

#----------------------------------------------------------------

# From Bin/Src/DB/DBInterfaces.cs (Jan2009)
# (In db.exe application)

def __Conn():
    m_sServer = Environment.MachineName + "\\SILFW"
    ##// Note: Integrated Security setting allows a database to be attached when the database was
    ##// detached with different credentials (e.g., Windows Authentication in Management Studio as
    ##// opposed to using the SA login). Unfortunately, on Vista if UAC is enabled, this fails.
    ##// See TE-6601 for details. Until this can be resolved, we've reverted all changes.
    ##// Changeset 23030 contains the changes that were made in addition to the one in InitMSDE
    ##// that David Olson made.
    sConnectionString = \
            "Server=" + m_sServer + "; Database=master; User ID = sa;" +\
            "Password=inscrutable; Pooling=false;"
    oConn = SqlConnection(sConnectionString)
    oConn.Open()
    return oConn


def ListFwDatabases():
    dbs = []
    ssql = "exec sp_GetFWDBs"
    oConn = __Conn()
    oCommand = SqlCommand(ssql, oConn)
    oReader = oCommand.ExecuteReader()
    while oReader.Read():
        dbs.append(oReader.GetString(0))
    return dbs
