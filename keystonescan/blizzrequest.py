'''
blizzrequest module docstring
'''

import requests

from keystonescan.blizzlocale import BlizzardLocale
from keystonescan.blizzregion import BlizzardRegion

class BlizzardApiError(Exception):
    '''
    Exception thrown when we get an bad return code from Blizzard API
    '''

class BlizzardThrottlingError(Exception):
    '''
    Exception thrown when we make too many requests
    '''

class BlizzardInvalidRegionError(Exception):
    '''
    Exception thrown when we get an unknown region
    '''

class BlizzardInvalidLocaleError(Exception):
    '''
    Exception thrown when we get a locale that's not supported
    '''

class BlizzardApiRequest:
    '''
    Wrapper for Blizzard API calls.
    '''
    _api_url_base = "https://{}.api.blizzard.com/{}"

    def __init__(self, oauth, region=BlizzardRegion.US, locale=BlizzardLocale.en_US):
        '''
        constructor
        '''
        if region not in BlizzardRegion:
            raise BlizzardInvalidRegionError("unknown region", region)
        if locale not in BlizzardLocale:
            raise BlizzardInvalidRegionError("unknown locale", locale)

        self.oauth = oauth

        self.locale = locale
        self.static_ns = "static-{}".format(region)
        self.dynamic_ns = "dynamic-{}".format(region)
        self.profile_ns = "profile-{}".format(region)

        self.profile_url_base = self._api_url_base.format(region, "profile/wow")
        self.data_url_base = self._api_url_base.format(region, "data/wow")

    def mythic_keystone_profile_detail(self, toon, season=6, **kwargs):
        '''
        Request a characters mythic keystone times for a specific season.
        '''
        url = "{}/character/{}/{}/mythic-keystone-profile/season/{}".format(
                self.profile_url_base, *toon.slug(), season)
        params = {"locale": kwargs.get("locale", self.locale)}
        headers = {
            "Authorization" : "Bearer {}".format(self.oauth.client_credentials()),
            "Battlenet-Namespace" : self.profile_ns,
        }
        resp = requests.get(url, params=params, headers=headers)

        # treat a 404 as missing data for that user.  In the beginning of a season
        # we can have no data for this specific user.
        if resp.status_code == 404:
            return {"best_runs":[]}

        if resp.status_code == 429:
            raise BlizzardThrottlingError(resp.text, resp.reason, resp.status_code, url)
        if resp.status_code != 200:
            raise BlizzardApiError(resp.text, resp.reason, resp.status_code, url)
        return resp.json()

    def mythic_keystone_dungeon_index(self, **kwargs):
        '''
        Return a list of mythic dungeons
        '''
        url = "{}/mythic-keystone/dungeon/index".format(self.data_url_base)
        params = {"locale": kwargs.get("locale", self.locale)}
        headers = {
            "Authorization" : "Bearer {}".format(self.oauth.client_credentials()),
            "Battlenet-Namespace" : self.dynamic_ns,
        }
        resp = requests.get(url, params=params, headers=headers)
        if resp.status_code == 429:
            raise BlizzardThrottlingError(resp.text, resp.status_code, url)
        if resp.status_code != 200:
            raise BlizzardApiError(resp.text, resp.status_code, url)
        return resp.json()

    def mythic_keystone_dungeon(self, dungeon_id, **kwargs):
        '''
        Return details on a specific mythic dungeon
        '''
        url = "{}/mythic-keystone/dungeon/{}".format(self.data_url_base, dungeon_id)
        params = {"locale": kwargs.get("locale", self.locale)}
        headers = {
            "Authorization" : "Bearer {}".format(self.oauth.client_credentials()),
            "Battlenet-Namespace" : self.dynamic_ns,
        }
        resp = requests.get(url, params=params, headers=headers)
        if resp.status_code == 429:
            raise BlizzardThrottlingError(resp.text, resp.status_code, url)
        if resp.status_code != 200:
            raise BlizzardApiError(resp.text, resp.status_code, url)
        return resp.json()

    def media_journal_instance(self, journal_id, **kwargs):
        '''
        Return details on a specific journal id
        '''
        url = "{}/media/journal-instance/{}".format(self.data_url_base, journal_id)
        params = {"locale": kwargs.get("locale", self.locale)}
        headers = {
            "Authorization" : "Bearer {}".format(self.oauth.client_credentials()),
            "Battlenet-Namespace" : self.static_ns,
        }
        resp = requests.get(url, params=params, headers=headers)
        if resp.status_code == 429:
            raise BlizzardThrottlingError(resp.text, resp.status_code, url)
        if resp.status_code != 200:
            raise BlizzardApiError(resp.text, resp.status_code, url)
        return resp.json()

    @classmethod
    def oauth_token_client(cls, client_id, client_secret, region=BlizzardRegion.US):
        '''
        Request a bearer token from blizzard using client credentials
        '''
        if region in (BlizzardRegion.US, BlizzardRegion.EU,):
            url = "https://{}.battle.net/oauth/token".format(region)
        elif region in (BlizzardRegion.KR, BlizzardRegion.TW):
            url = "https://apac.battle.net/oauth/token"
        elif region == BlizzardRegion.CN:
            url = "https://www.battlenet.com.cn/oauth/token"
        else:
            raise BlizzardInvalidRegionError("unknown region", region)

        resp = requests.post(url, data={'grant_type':'client_credentials'},
                auth=(client_id, client_secret))
        if resp.status_code == 429:
            raise BlizzardThrottlingError(resp.text, resp.status_code)
        if resp.status_code != 200:
            raise BlizzardApiError(resp.text, resp.status_code, url)
        return resp.json()

    @classmethod
    def oauth_check_token(cls, token, region=BlizzardRegion.US):
        if region in (BlizzardRegion.US, BlizzardRegion.EU,):
            url = "https://{}.battle.net/oauth/check_token".format(region)
        elif region in (BlizzardRegion.KR, BlizzardRegion.TW):
            url = "https://apac.battle.net/oauth/check_token"
        elif region == BlizzardRegion.CN:
            url = "https://www.battlenet.com.cn/oauth/check_token"
        else:
            raise BlizzardInvalidRegionError("unknown region", region)

        resp = requests.post(url, data={'token':token})
        return resp.status_code == 200

