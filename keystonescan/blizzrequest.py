'''
blizzrequest module docstring
'''

import requests

class BlizzardApiError(Exception):
    '''
    Exception thrown when we get an bad return code from Blizzard API
    '''

class BlizzardThrottlingError(Exception):
    '''
    Exception thrown when we make too many requests
    '''

def oauth_token_client(client_id, client_secret):
    '''
    Request a bearer token from blizzard using client credentials
    '''
    resp = requests.post("https://us.battle.net/oauth/token",
            data={'grant_type':'client_credentials'}, auth=(client_id, client_secret))
    if resp.status_code == 429:
        raise BlizzardThrottlingError(resp.json, resp.status_code)
    if resp.status_code != 200:
        raise BlizzardApiError(resp.json(), resp.status_code)
    return resp.json()

class BlizzardApiRequest():
    '''
    Wrapper for Blizzard API calls.
    '''
    profile_url_base = "https://us.api.blizzard.com/profile/wow"
    data_url_base = "https://us.api.blizzard.com/data/wow"

    def __init__(self, oauth):
        '''
        constructor
        '''
        self.oauth = oauth

    def mythic_keystone_profile_detail(self, toon, season=4):
        '''
        Request a characters mythic keystone times for a specific season.
        '''
        url = "{}/character/{}/{}/mythic-keystone-profile/season/{}".format(
                self.profile_url_base, *toon.slug(), season)
        params = {"locale":"en_US"}
        headers = {
            "Authorization" : "Bearer {}".format(self.oauth.client_credentials()),
            "Battlenet-Namespace" : "profile-us"
        }
        resp = requests.get(url, params=params, headers=headers)
        if resp.status_code == 429:
            raise BlizzardThrottlingError(resp.json, resp.status_code)
        if resp.status_code != 200:
            raise BlizzardApiError(resp.json(), resp.status_code)
        return resp.json()

    def mythic_keystone_dungeon_index(self):
        '''
        Return a list of mythic dungeons
        '''
        url = "{}/mythic-keystone/dungeon/index".format(self.data_url_base)
        params = {"locale":"en_US"}
        headers = {
            "Authorization" : "Bearer {}".format(self.oauth.client_credentials()),
            "Battlenet-Namespace" : "dynamic-us"
        }
        resp = requests.get(url, params=params, headers=headers)
        if resp.status_code == 429:
            raise BlizzardThrottlingError(resp.json, resp.status_code)
        if resp.status_code != 200:
            raise BlizzardApiError(resp.json(), resp.status_code)
        return resp.json()

    def mythic_keystone_dungeon(self, dungeon_id):
        '''
        Return details on a specific mythic dungeon
        '''
        url = "{}/mythic-keystone/dungeon/{}".format(self.data_url_base, dungeon_id)
        params = {"locale":"en_US"}
        headers = {
            "Authorization" : "Bearer {}".format(self.oauth.client_credentials()),
            "Battlenet-Namespace" : "dynamic-us"
        }
        resp = requests.get(url, params=params, headers=headers)
        if resp.status_code == 429:
            raise BlizzardThrottlingError(resp.json, resp.status_code)
        if resp.status_code != 200:
            raise BlizzardApiError(resp.json(), resp.status_code)
        return resp.json()

    def media_journal_instance(self, journal_id):
        '''
        Return details on a specific journal id
        '''
        url = "{}/media/journal-instance/{}".format(self.data_url_base, journal_id)
        params = {"locale":"en_US"}
        headers = {
            "Authorization" : "Bearer {}".format(self.oauth.client_credentials()),
            "Battlenet-Namespace" : "static-us"
        }
        resp = requests.get(url, params=params, headers=headers)
        if resp.status_code == 429:
            raise BlizzardThrottlingError(resp.json, resp.status_code, url)
        if resp.status_code != 200:
            raise BlizzardApiError(resp.json(), resp.status_code, url)
        return resp.json()
