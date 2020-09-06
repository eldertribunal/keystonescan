'''
toons module docstring
'''

import os
import json

class Toon():
    '''
    Toon docstring
    '''
    def __init__(self, player, realm, name):
        '''
        Toon constructor
        '''
        self.player = player
        self.realm = realm
        self.name = name
        self.keystone = {}

    def __repr__(self):
        '''
        repr
        '''
        return str(self)

    def __str__(self):
        '''
        str
        '''
        return '{{"{}":"{}/{}"}}'.format(self.player, self.realm, self.name)

    def slug(self):
        '''
        slug
        '''
        return (self.realm, self.name)

    def get_mythic_keystone(self, blizzapi):
        '''
        get_mythic_keystone
        '''
        keystone_detail = blizzapi.mythic_keystone_profile_detail(self)
        for run in keystone_detail["best_runs"]:
            lvl = run["keystone_level"]
            dung = run["dungeon"]["name"]
            timed = run["is_completed_within_time"]
            if timed:
                self.keystone[dung] = lvl

    @staticmethod
    def scan(input_dir):
        '''
        scan
        '''
        scan_toons = []
        with open(os.path.join(input_dir, "toons.json")) as toon_fd:
            toons_data = json.load(toon_fd)
            for player, toons in toons_data.items():
                for realm, characters in toons.items():
                    for name in characters:
                        scan_toons.append(Toon(player, realm, name))

        return scan_toons
