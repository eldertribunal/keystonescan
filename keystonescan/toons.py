'''
toons module docstring
'''

import os
import json
import logging

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
        self.keystone_score = 0
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

    def get_mythic_keystone(self, raiderioapi):
        '''
        get_mythic_keystone
        '''
        keystone_best = raiderioapi.mythic_plus_best_runs(self)
        keystone_alternate = raiderioapi.mythic_plus_alternate_runs(self)
        keystone_total_score = raiderioapi.mythic_plus_scores_by_season(self)

        if "mythic_plus_scores_by_season" in keystone_total_score:
            self.keystone_score = keystone_total_score["mythic_plus_scores_by_season"][0]["scores"]["all"]

        for run in keystone_best["mythic_plus_best_runs"]:
            dungeon = run["dungeon"]
            fort_tyr_affix = str.lower(run["affixes"][0]["name"])

            self.keystone[dungeon] = {
                "name": dungeon,
                "level": run["mythic_level"],
                "duration": run["clear_time_ms"],
                "rating": {
                    "fortified": 0,
                    "tyrannical": 0
                }
            }
            self.keystone[dungeon]["rating"][fort_tyr_affix] = run["score"]

        for run in keystone_alternate["mythic_plus_alternate_runs"]:
            dungeon = run["dungeon"]
            fort_tyr_affix = str.lower(run["affixes"][0]["name"])

            self.keystone[dungeon]["rating"][fort_tyr_affix] = run["score"]
        
        for dungeon in self.keystone.values():
            logging.info(dungeon)
            total = 0
            if dungeon["rating"]["fortified"] > dungeon["rating"]["tyrannical"]:
                total = dungeon["rating"]["fortified"] * 1.5 + dungeon["rating"]["tyrannical"] / 2.0
            else:
                total = dungeon["rating"]["tyrannical"] * 1.5 + dungeon["rating"]["fortified"] / 2.0
            dungeon["rating"]["total"] = round(total)

    def get_weekly_keystone(self, raiderioapi):
        '''
        get_weekly_keystone
        '''
        keystone_detail = raiderioapi.mythic_keystone_weekly_highest(self)

        # number of keys you need to complete for 3 vault choices.
        three_vault_choices=8

        for weekly_key in keystone_detail["mythic_plus_weekly_highest_level_runs"]:
            self.weekly_completed_keys.append(weekly_key["mythic_level"])
        self.weekly_completed_keys.sort(reverse=True)
        self.weekly_completed_keys = self.weekly_completed_keys[:three_vault_choices]
        padding = min(three_vault_choices, len(self.weekly_completed_keys))
        self.weekly_completed_keys.extend([0 for n in range(three_vault_choices - padding)])

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
