#!/usr/bin/env python3

'''
keystonescan
Pull down keystone activity for players and theirs various characters.  Output the
data in a parsable format, used to display on our guild page.
'''

import os
import json
import copy
import datetime
from datetime import timezone

from keystonescan.blizzoauth import BlizzOAuth
from keystonescan.blizzrequest import BlizzardApiRequest

from keystonescan import toons

class AuthorizationError(Exception):
    '''
    Exception with getting API credentials from access.json
    '''

def get_dungeon_defaults(blizzapi):
    '''
    Pull the current season dungeons and set the level completed to zero.
    This makes sure all toons have the same dungeon order when scanning
    their keystones completed.
    '''
    dungeon_default = []
    mythic_dungeons = blizzapi.mythic_keystone_dungeon_index()
    for mythic_dungeon in mythic_dungeons["dungeons"]:
        dungeon = blizzapi.mythic_keystone_dungeon(mythic_dungeon["id"])
        dungeon_default.append({
            "name": dungeon["name"],
            "level": 0,
            "id": dungeon["id"]
        })
    return dungeon_default

def scan_completed_keystones(blizzapi, scanned_toons):
    '''
    Get all toons from `<input_dir>/toons.json and query the blizzard API
    for all the completed keystones.

    {
        "Player": {
            "Atal Dazzar": 15,
            "Kings' Rest": 12,
        }
    }
    '''
    players = {}
    for toon in scanned_toons:
        print("scanning {}".format(toon))
        toon.get_mythic_keystone(blizzapi)
        if toon.player in players:
            for dungeon, lvl in toon.keystone.items():
                if dungeon not in players[toon.player] or players[toon.player][dungeon] < lvl:
                    players[toon.player][dungeon] = lvl
        else:
            players[toon.player] = toon.keystone
    return players

def get_toons(input_dir):
    '''
    Scan `<input_dir>/toons.json` for list of characters to scan.
    '''
    return toons.Toon.scan(input_dir)

def get_api_access_file(input_dir):
    '''
    Open `<input_dir>/access.json` to get the API client_id and client_secret
    '''
    access = {}
    try:
        with open(os.path.join(input_dir, 'access.json'), mode="r") as secret_fd:
            access = json.load(secret_fd)
    except FileNotFoundError as fnfe:
        raise AuthorizationError("Blizzard API access secrets file missing",
                os.path.join(input_dir, "access.json")) from fnfe

    if "client_id" not in access or "client_secret" not in access:
        raise AuthorizationError("Missing secrets values in access.json")

    return (access["client_id"], access["client_secret"])


def scan(input_dir, output_dir):
    '''
    Scan all the characters and write the formatted data to <output_dir>
    '''
    now = int(datetime.datetime.now(tz=timezone.utc).timestamp())

    blizzapi = BlizzardApiRequest(BlizzOAuth(*get_api_access_file(input_dir),
            os.path.join(input_dir, "auth_cache.json")))

    dungeon_default = get_dungeon_defaults(blizzapi)
    players = scan_completed_keystones(blizzapi, get_toons(input_dir))

    norm_players = []
    for player, dungeons in players.items():
        norm_player = {
            "name": player,
            "dungeons": copy.deepcopy(dungeon_default),
        }
        for norm_dungeon in norm_player["dungeons"]:
            if norm_dungeon["name"] in dungeons:
                norm_dungeon["level"] = dungeons[norm_dungeon["name"]]
        norm_players.append(norm_player)

    with open(os.path.join(output_dir, "players.json"), mode="w") as players_fd:
        json.dump(norm_players, players_fd, indent=2)

    with open(os.path.join(output_dir, "scanned.json"), mode="w") as scanned_fd:
        json.dump({"timestamp": now}, scanned_fd, indent=2)

    return 0
