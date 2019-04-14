import sys
import utils
import treasures
import itertools

class Actor:
    # base class for Enemy and Hero
    # all instances of Actor should provide the following attributes:
    # - health
    # - max_health
    # - mana
    # - max_mana
    # - pos: a valid position within the map
    # - weapon
    # - spell
    # - fist_damage
    
    @property
    def is_alive(self):
        return self.health != 0

    @property
    def can_cast(self):
        return self.mana != 0
    
    def heal(self, healing_points):
        if not self.is_alive:
            raise ValueError('cannot heal a dead actor')
        else:
            self.health = min(self.max_health, self.health + healing_points)
            return True
        
    def give_mana(self, mana_points):
        self.mana = min(self.max_mana, self.mana + mana_points)

    def take_mana(self, mana_points):
        self.mana = max(0, self.mana - mana_points)
        
    def damage(self, damage_points):
        self.health = max(0, self.health - damage_points)
        
    def equip(self, weapon):
        self.weapon = weapon

    def learn(self, spell):
        self.spell = spell
            
                            
class Hero(Actor):
    # a Hero has the following additional attributes:
    # - name
    # - title

    @staticmethod
    def from_dict(dct):
        # the dict must have the keys
        # {'name', 'title', 'health', 'mana', 'mana_regeneration_rate', 'fist_damage', 'pos'}
        result = object.__new__(Hero)
        result.name = dct['name']
        result.title = dct['title']
        result.health = result.max_health = dct['health']
        result.mana = result.max_mana = dct['mana']
        result.mana_regeneration_rate = dct['mana_regeneration_rate']
        result.fist_damage = dct['fist_damage']
        result.pos = dct['pos']
        result.weapon = treasures.Weapon()
        result.spell = treasures.Spell()
        return result
    
    @property
    def known_as(self):
        return f"{self.name} the {self.title}"

class Enemy(Actor):
    # additional attributes:
    #  - last_seen: the position the hero was last seen in.
    #  - hero_direction: always equal to utils.relative_direction(self.pos, self.last_seen);
    #                    it is included only for convenience.    

    @staticmethod
    def from_dict(dct):
        # @dct must have the keys
        # {'health', 'mana', 'fist_damage', 'pos', 'behavior'}
        result = object.__new__(Enemy)
        result.health = result.max_health = dct['health']
        result.mana = result.max_mana = dct['mana']
        result.fist_damage = dct['fist_damage']
        result.pos = dct['pos']
        result.behavior = dct['behavior']
        result.weapon = treasures.Weapon()
        result.spell = treasures.Spell()
        result.last_seen = result.hero_direction = None
        return result
        
