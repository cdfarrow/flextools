#
#   Project: FlexTools
#   Module:  FTReport
#
#   Report collater for FlexTools Modules:
#    - A new instance is passed to each Module's Run() method.
#    - The Module reports:
#        - Blank: A blank line with no icon
#        - Information: general status information
#        - Warning: a warning message, with optional FLEx reference
#        - Error: an error message, with optional FLEx reference
#    - The UI displays this report information to the user.
#
#   Craig Farrow
#   Oct 2008
#   v0.00
#

# ------------------------------------------------------------------

class FTReporter(object):
    INFO    = 0
    WARNING = 1
    ERROR   = 2
    BLANK   = 3

    def __init__(self):
        self.__handler = None
        self.__progressHandler = None
        self.Reset()

    def RegisterProgressHandler(self, handler):
        if handler:
            self.__progressHandler = handler
            self.progressMax = 0
            
    def RegisterUIHandler(self, handler):
        if handler:
            self.__handler = handler

    def Reset(self):
        self.messageCounts = [0,0,0,0]
        self.messages = []

    def __Report(self, msgType, msg, ref):
        self.messages.append((msgType, msg, ref))
        self.messageCounts[msgType] += 1
        if self.__handler:
            self.__handler(self.messages[-1])

    # --- Public methods for FTModules to use

    # > Messages

    def Blank(self):
        self.__Report(self.BLANK, None, None)
        
    def Info(self, msg, ref=None):
        self.__Report(self.INFO, msg, ref)

    def Warning(self, msg, ref=None):
        self.__Report(self.WARNING, msg, ref)

    def Error(self, msg, ref=None):
        self.__Report(self.ERROR, msg, ref)

    # > Progress Bar

    def ProgressUpdate(self, value):
        if self.__progressHandler:
            self.__progressHandler(value+1, 
                                   self.progressMax, 
                                   self.progressMessage)

    def ProgressStart(self, max, msg=None):
        self.progressMax = max
        self.progressMessage = msg
        self.ProgressUpdate(-1)
           
    def ProgressStop(self):
        self.progressMax = 0            # Stop signal
        self.progressMessage = ""
        self.ProgressUpdate(-1)
           
            
if __name__ == '__main__':
    f = FTReporter()
    f.Info("Hi")
    f.Blank()
    f.Warning("Cows crossing")
    f.Error("Bad bad news!")
    print(f.messageCounts)
    print(f.messages)
    
