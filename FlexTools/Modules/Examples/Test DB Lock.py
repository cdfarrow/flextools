# -*- coding: utf-8 -*-
#
#

from FTModuleClass import *


#----------------------------------------------------------------
# Documentation for the user:

docs = {'moduleName'       : "Test DB Lock",
        'moduleVersion'    : 2,
        'moduleModifiesDB' : True,
        'moduleSynopsis'   : "",
        'moduleDescription'   :
u"""
""" }


#from ChineseUtilities import ChineseWritingSystems, ChineseParser

                 
#----------------------------------------------------------------
# The main processing function

def Main(DB, report, modify=False):


    return
    

#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:

FlexToolsModule = FlexToolsModuleClass(runFunction = Main,
                                       docs = docs)
            

#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
