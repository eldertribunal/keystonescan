'''
keystonescan.blizzlocale
~~~~~~~~~~~~~~~~~~~~~~~~

This module provides locale support for Blizzard API
'''

class BlizzardLocaleMeta(type):
    '''
    Treat BlizzardLocale like a container so that we can do and easy
    locale check with `if "xxx" not in BlizzardLocale:`
    '''
    def __contains__(cls, item):
        '''
        Iterate over all the class variables defined in BlizzardLocale
        to check if the locale is supported.
        '''
        for var in vars(BlizzardLocale):
            # skip over any class vars that look like special python
            # variables like __module__, __doc__, __dict__ and __weakref__
            if var.startswith("__") and var.endswith("__"):
                continue
            # from what I can tell, var is the string name of the variable
            # what we want is the contents of the variable
            if BlizzardLocale.__dict__[var] == item:
                return True
        return False

class BlizzardLocale(metaclass=BlizzardLocaleMeta): # pylint: disable=too-few-public-methods
    '''
    Supported locales used in Blizzard API calls.

    Basic Usage::
       >>> req = BlizzardApiRequest(None, locale=BlizzardLocale.es_MX)
       >>> req.get_mythic_keystone(locale=BlizzardLocale.it_IT)
       <some json>
    '''
    en_US = "en_US"
    es_MX = "es_MX"
    pt_BR = "pt_BR"
    de_DE = "de_DE"
    en_GB = "en_GB"
    es_ES = "es_ES"
    fr_FR = "fr_FR"
    it_IT = "it_IT"
    ru_RU = "ru_RU"
    ko_KR = "ko_KR"
    zh_TW = "zh_TW"
    zh_CN = "zh_CN"
