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
    # - map
    # - pos: a valid position within map    
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
        if not self.is_alive:
            self.map.cleanup_at(self.pos)

    def equip(self, weapon):
        self.weapon = weapon

    def learn(self, spell):
        self.spell = spell
            
    def do_turn(self):
        # called when it is the actor's turn
        raise NotImplementedError

    def move(self, direction):
        # @direction must be one of {'up', 'down', 'left', 'right'}
        # if it is possible to move the actor in @direction, moves him and returns True;
        # otherwise, return False
    
        new_pos = utils.move_pos(self.pos, direction)
        
        if not self.map.can_move_to(new_pos):
            return

        if self.map.contains_treasure_at(new_pos):
            self.map[new_pos].open().give_to_actor(self)

        # at this point self.map[pos] contains a walkable.
        # swap the walkable with self
        self.map[self.pos] = '.'
        self.map[new_pos] = self
        self.pos = new_pos

    def attack(self, by, direction):
        # @by must be in {'weapon', 'spell', 'fist'}
        # @direction must be in {'up', 'down', 'left', 'right'}

        if by == 'spell':
            spell = self.spell
            
            if self.mana < spell.mana_cost:
                return

            self.take_mana(spell.mana_cost)
            
            for pos in itertools.islice(self.map.positions(self.pos, direction), spell.cast_range):
                entity = self.map[pos]
                if isinstance(entity, Actor):
                    entity.damage(spell.damage)
                    break
                elif entity != '.':
                    break
        else:
            # by is in {'weapon', 'fist'}
            nemesis_pos = next(self.map.positions(self.pos, direction), None)
            
            if nemesis_pos is None:
                return
            
            nemesis = self.map[nemesis_pos]
            
            if not isinstance(nemesis, Actor):
                return

            damage = self.weapon.damage if by == 'weapon' else self.fist_damage
            nemesis.damage(damage)
                            
class Hero(Actor):
    # a Hero has the following additional attributes:
    # - name
    # - title

    @staticmethod
    def from_dict(dct):
        # the dict must have the keys
        # {'name', 'title', 'health', 'mana', 'fist_damage', 'map', 'pos'}
        result = object.__new__(Hero)
        result.name = dct['name']
        result.title = dct['title']
        result.health = result.max_health = dct['health']
        result.mana = result.max_mana = dct['mana']
        result.fist_damage = dct['fist_damage']
        result.pos = dct['pos']
        result.map = dct['map']
        result.weapon = treasures.Weapon()
        result.spell = treasures.Spell()
        return result
    
    @property
    def known_as(self):
        return f"{self.name} the {self.title}"

    def display(self):
        print(f'health: {self.health}')
        print(f'mana: {self.mana}')
        print(f'weapon: {self.weapon.name}')
        print(f'spell: {self.spell.name}')
        print()
    
    def read_command(self):
        # returns one of:
        # {'up', 'down', 'left', 'right',
        #  ('weapon', 'up'), ..., ('weapon', 'right'),
        #  ('fist', 'up'), ..., ('fist', 'right'),
        #  ('spell', 'up', ...', ('spell', 'right')}
        # TODO: handle user chars better
        # THIS FUNCTION DETERMINES THE USER CONTROL KEYS

        while True:
            first_char = utils.get_char()
            if first_char in '2468':
                return {'2': 'down', '4': 'left', '6': 'right', '8': 'up'}[first_char]
            elif first_char in 'wsf':
                by = {'w': 'weapon', 's': 'spell', 'f': 'fist'}[first_char]
                second_char = utils.get_char()
                if second_char not in '2468':
                    continue
                direction = {'2': 'down', '4': 'left', '6': 'right', '8': 'up'}[second_char]
                return by, direction
                
    def do_turn(self):
        command = self.read_command()
        if type(command) is str:
            # command is one of {'up', 'down', 'left', 'right'}
            self.move(command)
        else:
            # command has the form (<kind of attack>, <direction>)
            self.attack(*command)
            
class Enemy(Actor):
    # additional attributes:
    #  - last_seen: the position the hero was last seen in.
    #  - hero_direction: always equal to utils.relative_direction(self.pos, self.last_seen);
    #                    it is included only for convenience.
    #  if the enemy does not know where the hero is, self.last_seen and
    #  self.hero_direction will both be None.

    @staticmethod
    def from_dict(dct):
        # @dct must have the keys
        # {'health', 'mana', 'fist_damage', 'pos', 'map'}
        result = object.__new__(Enemy)
        result.health = result.max_health = dct['health']
        result.mana = result.max_mana = dct['mana']
        result.fist_damage = dct['fist_damage']
        result.pos = dct['pos']
        result.map = dct['map']
        result.weapon = treasures.Weapon()
        result.spell = treasures.Spell()
        result.last_seen = result.hero_direction = None
        return result
        
    def search_for_hero(self):
        # returns the position of the hero, or None if he can't be seen
        # @self will only look up, down, left and right

        def try_direction(direction):
            # looks for the hero in the direction @direction
            # returns None if @self can't see him in that direction
            
            for pos in self.map.positions(self.pos, direction):
                entity = self.map[pos]
                if type(entity) is Hero:
                    return pos
                elif entity != '.':
                    # something blocks @self's view
                    return None
            return None

        for direction in ('up', 'down', 'left', 'right'):
            pos = try_direction(direction)
            if pos is not None:
                return pos, direction
            
        return None, None
        
    def move_to_last_seen(self):
        if self.last_seen is None:
            return

        if self.pos == self.last_seen:
            self.last_seen = None
            self.hero_direction = None
            return

        self.move(self.hero_direction)
    
    def do_turn(self):
        def hero_is_in_vicinity():
            # Returns True if hero is directly above, below, to the right
            # or to the left of @self.
            pos_row, pos_col = self.pos
            hero_row, hero_col = hero_pos
            return abs(pos_row - hero_row) <= 1 and abs(pos_col - hero_col) <= 1

        def attack_hero():
            # Call only when the hero is next to @self!
            # The enemy determines the attack type dealing the most
            # damage and inflicts it on the hero.
            self.attack('fist', self.hero_direction)
        
        hero_pos, hero_direction = self.search_for_hero()
        if hero_pos is None:
            # the enemy cannot see the hero
            self.move_to_last_seen()
        else:
            self.last_seen = hero_pos
            self.hero_direction = hero_direction
            if hero_is_in_vicinity():
                attack_hero()
            else:
                self.move_to_last_seen()
