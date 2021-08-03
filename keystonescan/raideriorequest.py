import requests

class RaiderIoApiError(Exception):
    '''
    Exception thrown when we get an bad return code from Blizzard API
    '''

class RaiderIoThrottlingError(Exception):
    '''
    Exception thrown when we make too many requests
    '''

class RaiderIoApiRequest:
    '''
    Wrapper for RaiderIO API calls.
    '''

    def __init__(self):
        '''
        constructor
        '''
        self.region = "us"
        self.url_base = "https://raider.io/api/v1"

    def mythic_keystone_weekly_highest(self, toon, **kwargs):
        '''
        Request a characters weekly highest keystone runs.
        '''
        url = "{}/characters/profile".format(self.url_base)
        params = {"region": kwargs.get("region", self.region),
                  "realm": toon.realm,
                  "name": toon.name,
                  "fields": "mythic_plus_weekly_highest_level_runs"}
        headers = {
            "accept": "application/json",
        }
        resp = requests.get(url, params=params, headers=headers)
        if resp.status_code == 429:
            raise RaiderIoThrottlingError(resp.text, resp.reason, resp.status_code, url)
        if resp.status_code != 200:
            raise RaiderIoApiError(resp.text, resp.reason, resp.status_code, url)

        return resp.json()

    def mythic_plus_best_runs(self, toon, **kwargs):
        '''
        Request a characters best dungeon runs.
        '''
        url = "{}/characters/profile".format(self.url_base)
        params = {"region": kwargs.get("region", self.region),
                  "realm": toon.realm,
                  "name": toon.name,
                  "fields": "mythic_plus_best_runs:all"}
        headers = {
            "accept": "application/json",
        }
        resp = requests.get(url, params=params, headers=headers)
        if resp.status_code == 429:
            raise RaiderIoThrottlingError(resp.text, resp.reason, resp.status_code, url)
        if resp.status_code != 200:
            raise RaiderIoApiError(resp.text, resp.reason, resp.status_code, url)

        return resp.json()

    def mythic_plus_alternate_runs(self, toon, **kwargs):
        '''
        Request a characters second best dungeon runs.
        '''
        url = "{}/characters/profile".format(self.url_base)
        params = {"region": kwargs.get("region", self.region),
                  "realm": toon.realm,
                  "name": toon.name,
                  "fields": "mythic_plus_alternate_runs:all"}
        headers = {
            "accept": "application/json",
        }
        resp = requests.get(url, params=params, headers=headers)
        if resp.status_code == 429:
            raise RaiderIoThrottlingError(resp.text, resp.reason, resp.status_code, url)
        if resp.status_code != 200:
            raise RaiderIoApiError(resp.text, resp.reason, resp.status_code, url)

        return resp.json()
