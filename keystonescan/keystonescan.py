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
from datetime import timedelta

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
        media = blizzapi.media_journal_instance(dungeon["dungeon"]["id"])
        upgrade_times = [str(timedelta(milliseconds=duration))
                for _, duration in [keystone_upgrades.values()
                    for keystone_upgrades in dungeon["keystone_upgrades"]]]
        upgrade_times.sort(reverse=True)
        tile = None
        for asset in media["assets"]:
            if asset["key"] == "tile":
                tile = asset["value"]
        dungeon_default.append({
            "name": dungeon["name"],
            "level": 0,
            "id": dungeon["id"],
            "upgrade": upgrade_times,
            "tile": tile
        })

    return dungeon_default

def scan_completed_keystones(blizzapi, scanned_toons):
    '''
    Get all toons from `<input_dir>/toons.json and query the blizzard API
    for all the completed keystones.
    '''
    for toon in scanned_toons:
        print("scanning {}".format(toon))
        toon.get_mythic_keystone(blizzapi)
    return scanned_toons

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


def generate_player_output(output_dir, characters, dungeon_default):
    '''
    generate_player_output
    '''
    # collapse all characters with the same player into a dictionary
    player_cache = {}
    for character in characters:
        if character.player not in player_cache:
            player_cache[character.player] = copy.deepcopy(dungeon_default)

        for dungeon in player_cache[character.player]:
            dname, dlevel, _, _, _ = dungeon.values()
            if dname in character.keystone and dlevel < character.keystone[dname]:
                dungeon["level"] = character.keystone[dname]

    with open(os.path.join(output_dir, "players.json"), mode="w") as players_fd:
        json.dump(
            [{"name": player, "dungeons": dungeons} for player, dungeons in player_cache.items()],
            players_fd, indent=2)

def generate_character_output(output_dir, characters, dungeon_default):
    '''
    generate_character_output
    '''
    character_cache = {}
    for character in characters:
        character_cache[character.name] = copy.deepcopy(dungeon_default)

        for dungeon in character_cache[character.name]:
            dname, dlevel, _, _, _ = dungeon.values()
            if dname in character.keystone and dlevel < character.keystone[dname]:
                dungeon["level"] = character.keystone[dname]

    with open(os.path.join(output_dir, "characters.json"), mode="w") as character_fd:
        json.dump(
            [{"name": str.capitalize(character), "dungeons": dungeons}
                    for character, dungeons in character_cache.items()],
            character_fd, indent=2)

def generate_dungeon_output(output_dir, dungeon_default):
    '''
    generate_dungeon_output
    '''
    with open(os.path.join(output_dir, "dungeons.json"), mode="w") as dungeon_fd:
        json.dump(dungeon_default, dungeon_fd, indent=2)


def scan(input_dir, output_dir):
    '''
    Scan all the characters and write the formatted data to <output_dir>
    '''
    now = int(datetime.datetime.now(tz=timezone.utc).timestamp())

    blizzapi = BlizzardApiRequest(BlizzOAuth(*get_api_access_file(input_dir),
            os.path.join(input_dir, "auth_cache.json")))

    dungeon_default = get_dungeon_defaults(blizzapi)
    characters = scan_completed_keystones(blizzapi, get_toons(input_dir))

    generate_player_output(output_dir, characters, dungeon_default)
    generate_character_output(output_dir, characters, dungeon_default)
    generate_dungeon_output(output_dir, dungeon_default)

    with open(os.path.join(output_dir, "scanned.json"), mode="w") as scanned_fd:
        json.dump({"timestamp": now}, scanned_fd, indent=2)

    return 0
