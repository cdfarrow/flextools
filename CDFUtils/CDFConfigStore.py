#
#   Module:  CDFConfig
#   Platform: Python 2.5
#
#   A generic configuration class that persists values in a text file.
#
#   TODO:
#
#   Craig Farrow
#   Oct 2010
#   v1
#

import ConfigParser

class CDFConfigStore(object):
    """
    A generic configuration class that persists the values in a text file.
    - A file name can be specified in the constructor, otherwise the
      default name "config.ini" is used.
    - Values are simply accessed as members of the class, e.g.:
           Config = CDFConfigStore()
           Config.username = "Fred"
           Config.email = "fred@rubble.com"
           DoSomething(Config.username, Config.email)
    - Undefined values default to None:
           >>> type(Config.notusedbefore)
           <type 'NoneType'>
    - Supports any native Python type.
    Limitations:
    - Values can be modified by assignment operations only. E.g.:
            Config.int += 1             # Works
            Config.list.append("new")   # Doesn't work
    """
    def __init__(self, fileName="config.ini"):
        object.__setattr__(self, "__FNAME", fileName)
        cp = ConfigParser.RawConfigParser()
        object.__setattr__(self, "__cp", cp)
        cp.read(object.__getattribute__(self, "__FNAME"))

    def __setattr__(self, key, value):
        cp = object.__getattribute__(self, "__cp")
        cp.set(ConfigParser.DEFAULTSECT, key, repr(value))

    def __getattr__(self, key):
        if key.startswith("__"):
            return object.__getattribute__(self, key)
        cp = object.__getattribute__(self, "__cp")
        if not cp.has_option(ConfigParser.DEFAULTSECT, key):
            cp.set(ConfigParser.DEFAULTSECT, key, None)
        val = cp.get(ConfigParser.DEFAULTSECT, key)
        if val is None:
            return None
        else:
            return eval(val)

    def __delattr__(self, key):
        cp = object.__getattribute__(self, "__cp")
        if cp.has_option(ConfigParser.DEFAULTSECT, key):
            cp.remove_option(ConfigParser.DEFAULTSECT, key)

    def items(self):
        """
        Get all the (item, value) pairs.
        """
        cp = object.__getattribute__(self, "__cp")
        return cp.items(ConfigParser.DEFAULTSECT)
    
    def __del__(self):
        f = open(object.__getattribute__(self, "__FNAME"), "w")
        cp = object.__getattribute__(self, "__cp")
        cp.write(f)
        f.close()
        

    

