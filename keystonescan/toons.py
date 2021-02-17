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
        self.keystone_details = {}
        self.weekly_completed_keys = []

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
            if run["is_completed_within_time"]:
                dungeon = run["dungeon"]["name"]
                self.keystone[dungeon] = run["keystone_level"]
                self.keystone_details[dungeon] = {
                    "level": run["keystone_level"],
                    "duration": run["duration"],
                    "affixes": [affix["name"] for affix in run["keystone_affixes"]],
                    "members": [],
                }

    def get_weekly_keystone(self, raiderioapi):
        '''
        get_weekly_keystone
        '''
        keystone_detail = raiderioapi.mythic_keystone_weekly_highest(self)

        for weekly_key in keystone_detail["mythic_plus_weekly_highest_level_runs"]:
            self.weekly_completed_keys.append(weekly_key["mythic_level"])
        self.weekly_completed_keys.sort(reverse=True)
        self.weekly_completed_keys = self.weekly_completed_keys[:10]
        padding = min(10, len(self.weekly_completed_keys))
        self.weekly_completed_keys.extend([0 for n in range(10 - padding)])

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
