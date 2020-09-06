'''
blizzoauth module docstring
'''
import json
import datetime
from datetime import timezone
from keystonescan import blizzrequest

class BlizzOAuth():
    '''
    BlizzOAuth class docstring
    '''
    def __init__(self, client_id, client_secret, auth_cache):
        '''
        constructor docstring
        '''
        self.client_id = client_id
        self.client_secret = client_secret
        self.auth_cache_file = auth_cache

    def __repr__(self):
        return str(self)

    def __str__(self):
        '''
        string val of class
        '''
        return "{}".format(self.client_id)

    def client_credentials(self):
        '''
        return oauth bearer token
        '''
        auth_cache = {}
        now = int(datetime.datetime.now(tz=timezone.utc).timestamp())

        # auth_cache.json contains:
        # {
        #    "<client_id value>": {
        #        "timestamp": <time when blizz request was made>,
        #        "access_token": "xyz",
        #        "token_type": "bearer",
        #        "expires_in": 86399
        #    }
        # }
        try:
            with open(self.auth_cache_file, mode="r") as auth_fd:
                auth_cache = json.load(auth_fd)
                if self.client_id in auth_cache:
                    auth_info = auth_cache[self.client_id]
                    if auth_info["timestamp"] + auth_info["expires_in"] > now:
                        return auth_info["access_token"]
        except FileNotFoundError:
            pass
        except json.decoder.JSONDecodeError:
            pass


        # we have a cache miss, call blizzard API and request new access_token
        token = blizzrequest.oauth_token_client(self.client_id, self.client_secret)
        token["timestamp"] = now
        with open(self.auth_cache_file, mode="w") as auth_fd:
            cache_entry = {
                self.client_id: token
            }
            auth_fd.write(json.dumps(cache_entry))
        return token["access_token"]
