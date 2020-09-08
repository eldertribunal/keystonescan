'''
keystonescan.blizzregion
~~~~~~~~~~~~~~~~~~~~~~~~

This module provides region support for Blizzard API
'''

class BlizzardRegionMeta(type):
    '''
    Treat BlizzardRegion like a container so that we can do and easy
    locale check with `if "xxx" not in BlizzardRegion:`
    '''
    def __contains__(cls, item):
        '''
        Iterate over all the class variables defined in BlizzardRegion
        to check if the region is supported.
        '''
        for var in vars(BlizzardRegion):
            # skip over any class vars that look like special python
            # variables like __module__, __doc__, __dict__ and __weakref__
            if var.startswith("__") and var.endswith("__"):
                continue
            # from what I can tell, var is the string name of the variable
            # what we want is the contents of the variable
            if BlizzardRegion.__dict__[var] == item:
                return True
        return False

class BlizzardRegion(metaclass=BlizzardRegionMeta): # pylint: disable=too-few-public-methods
    '''
    Supported regions used in Blizzard API calls.

    Basic Usage::
       >>> req = BlizzardApiRequest(None, BlizzardRegion.EU)
       >>> req.static_ns
       "static-eu"
    '''
    US = "us"
    EU = "eu"
    KR = "kr"
    TW = "tw"
    CN = "cn"
