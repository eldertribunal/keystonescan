'''
Dungeon information
'''

import os
import json

class Dungeon():
    '''
    Class wrapper for dungeon info pulled from wow api sources.
    '''
    def __init__(self, name, level=0, time=0):
        '''
        Dungeon constructor
        '''
        self.name = name
        self.level = level
        self.time = time
        self.score = 0
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
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return isinstance(other, self) and self.name == other.name

    def slug(self):
        '''
        slug
        '''
        return (self.realm, self.name)
