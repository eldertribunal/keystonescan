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
import operator
import logging

from keystonescan.blizzoauth import BlizzOAuth
from keystonescan.blizzrequest import BlizzardApiRequest
from keystonescan.raideriorequest import RaiderIoApiRequest, RaiderIoApiError

from keystonescan import toons

class AuthorizationError(Exception):
    '''
    Exception with getting API credentials from access.json
    '''

def get_dungeon_details(blizzapi, mythic_dungeons):
    '''
    Pull down dungeon detailed information like the dungeon background image
    and keystone upgrade times.
    '''
    dungeon_details = []
    for mythic_dungeon in mythic_dungeons:
        dungeon = blizzapi.mythic_keystone_dungeon(mythic_dungeon["id"])
        upgrade_times = [str(timedelta(milliseconds=duration))
                for _, duration in [keystone_upgrades.values()
                    for keystone_upgrades in dungeon["keystone_upgrades"]]]
        upgrade_times.sort(reverse=True)

        media = blizzapi.media_journal_instance(dungeon["dungeon"]["id"])
        tile = None
        for asset in media["assets"]:
            if asset["key"] == "tile":
                tile = asset["value"]

        dungeon_details.append({
            "name": dungeon["name"],
            "id": dungeon["id"],
            "upgrade": upgrade_times,
            "tile": tile,
        })

    sorted(dungeon_details, key=operator.itemgetter("id"))
    return dungeon_details

def get_dungeon_defaults(blizzapi, exclusions=[197, 198, 199, 206, 207, 210]):
    '''
    Pull the current season dungeons and set the level completed to zero.
    This makes sure all toons have the same dungeon order when scanning
    their keystones completed.

    @param exclusions List of dungeon ids to ignore during the scan
    '''
    dungeon_default = []
    mythic_dungeons = blizzapi.mythic_keystone_dungeon_index()
    for mythic_dungeon in mythic_dungeons["dungeons"]:
        if mythic_dungeon["id"] not in exclusions:
            dungeon_default.append({
                "id": mythic_dungeon["id"],
                "name": mythic_dungeon["name"],
                "level": 0,
                "duration":0,
                "rating": {
                    "total": 0,
                    "tyrannical": 0,
                    "fortified": 0
                }
            })

    sorted(dungeon_default, key=operator.itemgetter("id"))
    return dungeon_default

def scan_completed_keystones(raiderioapi, scanned_toons):
    '''
    Get all toons from `<input_dir>/toons.json and query the blizzard API
    for all the completed keystones.
    '''
    for toon in scanned_toons:
        logging.info("scanning {}".format(toon))
        try:
            toon.get_mythic_keystone(raiderioapi)
        except RaiderIoApiError as err:
            if err.args[0] == 400 and err.args[1] == "Bad Request":
                logging.error(err)
            else:
                raise err
    return scanned_toons

def scan_weekly_keystones(raiderioapi, scanned_toons):
    '''
    Get all toons from `<input_dir>/toons.json and query the blizzard API
    for keystons complete this week.
    '''
    for toon in scanned_toons:
        toon.get_weekly_keystone(raiderioapi)
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

def generate_weekly_output(output_dir, characters, dungeon_default):
    character_cache = {}
    for character in characters:
        character_cache[character.name] = character.weekly_completed_keys

    with open(os.path.join(output_dir, "weekly.json"), mode="w") as character_fd:
        json.dump(
            [{"name": str.capitalize(character), "dungeons": dungeons}
                    for character, dungeons in character_cache.items()],
            character_fd, indent=2)

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
            if dungeon["name"] in character.keystone and dungeon["level"] < character.keystone[dungeon["name"]]["level"]:
                dungeon["level"] = character.keystone[dungeon["name"]]["level"]
                dungeon["duration"] = character.keystone[dungeon["name"]]["duration"]
                dungeon["rating"] = character.keystone[dungeon["name"]]["rating"]

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
            if dungeon["name"] in character.keystone:
                dungeon["level"] = character.keystone[dungeon["name"]]["level"]
                dungeon["duration"] = character.keystone[dungeon["name"]]["duration"]
                dungeon["rating"] = character.keystone[dungeon["name"]]["rating"]

    with open(os.path.join(output_dir, "characters.json"), mode="w") as character_fd:
        json.dump(
            [{"name": str.capitalize(character), "dungeons": dungeons}
                    for character, dungeons in character_cache.items()],
            character_fd, indent=2)

def generate_dungeon_output(output_dir, dungeon_details):
    '''
    generate_dungeon_output
    '''
    with open(os.path.join(output_dir, "dungeons.json"), mode="w") as dungeon_fd:
        json.dump(dungeon_details, dungeon_fd, indent=2)


def scan(input_dir, output_dir, character=False, player=False, dungeon=False, weekly=False, debug=False):
    '''
    Scan all the characters and write the formatted data to <output_dir>
    '''

    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.INFO)

    now = int(datetime.datetime.now(tz=timezone.utc).timestamp())

    blizzapi = BlizzardApiRequest(BlizzOAuth(*get_api_access_file(input_dir),
            os.path.join(input_dir, "auth_cache.json")))
    raiderioapi = RaiderIoApiRequest()

    dungeon_default = get_dungeon_defaults(blizzapi)

    if player or character:
        characters = scan_completed_keystones(raiderioapi, get_toons(input_dir))

    if player:
        generate_player_output(output_dir, characters, dungeon_default)

    if character:
        generate_character_output(output_dir, characters, dungeon_default)

    if dungeon:
        dungeon_details = get_dungeon_details(blizzapi, dungeon_default)
        generate_dungeon_output(output_dir, dungeon_details)
    
    if weekly:
        characters = scan_weekly_keystones(raiderioapi, get_toons(input_dir))
        generate_weekly_output(output_dir, characters, dungeon_default)

    with open(os.path.join(output_dir, "scanned.json"), mode="w") as scanned_fd:
        json.dump({"timestamp": now}, scanned_fd, indent=2)

    return 0
