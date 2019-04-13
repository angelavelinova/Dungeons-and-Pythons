import json
import copy
import treasures
import actors
import os
import itertools
import utils
import sys
import time

class Map:
    WALKABLE = '.'
    ENEMY = 'E'
    GATEWAY = 'G'
    TREASURE_CHEST = 'T'
    HERO = 'H'
    OBSTACLE = '#'
    NORTH_BORDER = '#'
    SOUTH_BORDER = '#'
    WEST_BORDER = '#'
    EAST_BORDER = '#'
    
    def __init__(self, matrix):
        self.matrix = matrix
                
    @property
    def nrows(self):
        return len(self.matrix)

    @property
    def ncols(self):
        return len(self.matrix[0])

    def cleanup_at(self, pos):
        self[pos] = self.WALKABLE

    def contains_treasure_at(self, pos):
        # returns True iff self[pos] is a treasure
        return isinstance(self[pos], treasures.TreasureChest)

    def pos_is_valid(self, pos):
        row, col = pos
        return row >= 0 and row < self.nrows and col >= 0 and col < self.ncols
        
    def can_move_to(self, pos):
        # returns True if pos is within @self and if there is nothing
        # at that position that prevents you from moving there.
        return (self.pos_is_valid(pos)
                and (isinstance(self[pos], treasures.TreasureChest)
                     or self[pos] is self.WALKABLE
                     or self[pos] is self.GATEWAY))
    
    @property
    def chars(self):
        result = []
        for row in range(self.nrows):
            lst = []
            for col in range(self.ncols):
                if isinstance(self[row,col], treasures.TreasureChest):
                    lst.append(self.TREASURE_CHEST)
                elif isinstance(self[row,col], actors.Hero):
                    lst.append(self.HERO)
                elif isinstance(self[row,col], actors.Enemy):
                    lst.append(self.ENEMY)
                else:
                    lst.append(self[row,col])
            result.append(lst)
        return result

    def __getitem__(self, pos):
        # pos must be a pair (<row-index>, <column-index>)
        row, col = pos
        return self.matrix[row][col]

    def __setitem__(self, pos, value):
        # pos must be a pair (<row-index>, <column-index>)
        row, col = pos
        self.matrix[row][col] = value
    
    def positions(self, pos, direction):
        while True:
            pos = utils.move_pos(pos, direction)
            if self.pos_is_valid(pos):
                yield pos
            else:
                break

    @property
    def posns_lrtb(self):
        # returns an iterator of the positions of self in the order
        # left to right, top to bottom
        for rowi in range(self.nrows):
            for coli in range(self.ncols):
                yield (rowi, coli)
    
    def neighbours(self, pos):
        # returns an iterator of the positions around @pos,
        # starting from the top left and going clockwise.
        
        def fits(pos):
            return 0 <= pos[0] < self.nrows and 0 <= pos[1] < self.ncols
        
        r, c = pos
        candidates = ((r-1, c-1), (r-1, c), (r-1, c+1),
                      (r, c-1), (r, c+1),
                      (r+1, c-1), (r+1, c), (r+1, c+1))
        
        return filter(fits, candidates)

class Game:
    WON = object()
    KILLED = object()
    QUIT = object()
    
    def __init__(self, hero, enemies, map):
        # @hero should be a Hero instance whose map is @map
        # @enemies should be a list of Enemy instances and each enemy's map should be @map
        # @map should be a Map instance
        
        self.hero = hero
        self.enemies = enemies
        self.map = map
        self.map_chars = map.chars

        # needed for restarting the game
        self.initial_state = copy.deepcopy(self.__dict__)

    @staticmethod
    def read_command():
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


    def move_actor(self, actor, direction):
        # @direction must be one of {'up', 'down', 'left', 'right'}
        # if it is possible to move the actor in @direction, moves him and returns True;
        # otherwise, return False
    
        new_pos = utils.move_pos(actor.pos, direction)
        
        if not self.map.can_move_to(new_pos):
            return

        if self.map.contains_treasure_at(new_pos):
            self.map[new_pos].open().give_to_actor(actor)
            self.map.cleanup_at(new_pos)

        # at this point self.map[pos] contains a walkable.
        # swap the walkable with self
        self.map[actor.pos] = self.map.WALKABLE
        self.map[new_pos] = actor
        actor.pos = new_pos

    def actor_attack(self, actor, by, direction):
        # @by must be in {'weapon', 'spell', 'fist'}
        # @direction must be in {'up', 'down', 'left', 'right'}

        SECS = 0.075 # needed for animation
        HIT = '*'
        
        def animate_spell_cast(posns, end):
            # end must be in {'actor', 'inanimate', 'evaporate'}
            # all posns until the last one must be walkable
            symbol = {'up': '^', 'down': 'v', 'left': '<', 'right': '>'}[direction]
            for pos in posns[:-1]:
                r, c = pos
                old_char = self.map_chars[r][c]
                self.map_chars[r][c] = symbol
                self.display()
                time.sleep(SECS)
                self.map_chars[r][c] = old_char
                
            r, c = posns[-1]
            if end == 'actor':
                self.map_chars[r][c] = HIT
            elif end == 'evaporate':
                print('evaporate')
                self.map_chars[r][c] = symbol
            else:
                pass
            self.display()
            time.sleep(SECS)

        def animate_melee(victim_pos):
            # call only if weapon or fist attack was actually made
            r, c = victim_pos
            self.map_chars[r][c] = HIT
            self.display()
            time.sleep(SECS)
        
        if by == 'spell':
            spell = actor.spell
            
            if actor.mana < spell.mana_cost:
                return

            actor.take_mana(spell.mana_cost)

            anim_posns = []
            for pos in itertools.islice(self.map.positions(actor.pos, direction), spell.cast_range):
                anim_posns.append(pos)
                entity = self.map[pos]
                if isinstance(entity, actors.Actor):
                    entity.damage(spell.damage)
                    self.remove_body_if_dead(entity)
                    animate_spell_cast(anim_posns, end='actor')
                    break
                elif entity != self.map.WALKABLE:
                    animate_spell_cast(anim_posns, 'other')
                    break
            else:
                animate_spell_cast(anim_posns, 'evaporate')
        else:
            # by is in {'weapon', 'fist'}
            victim_pos = next(self.map.positions(actor.pos, direction), None)
            
            if victim_pos is None:
                return
            
            victim = self.map[victim_pos]
            
            if not isinstance(victim, actors.Actor):
                return

            damage = actor.weapon.damage if by == 'weapon' else actor.fist_damage
            victim.damage(damage)
            self.remove_body_if_dead(victim)
            animate_melee(victim_pos)

    def remove_body_if_dead(self, actor):
        if not actor.is_alive:
            self.map.cleanup_at(actor.pos)

    def hero_turn(self):
        hero = self.hero
        command = self.read_command()
        if type(command) is str:
            # command is one of {'up', 'down', 'left', 'right'}
            self.move_actor(hero, command)
        else:
            # command has the form (<kind of attack>, <direction>)
            self.actor_attack(hero, *command)
        hero.give_mana(hero.mana_regeneration_rate)

    def enemy_turn(self, enemy):
        def search_for_hero():
            # returns the position of the hero, or None if he can't be seen
            # @enemy will only look up, down, left and right

            def try_direction(direction):
                # looks for the hero in the direction @direction
                # returns None if @enemy can't see him in that direction

                for pos in self.map.positions(enemy.pos, direction):
                    entity = self.map[pos]
                    if type(entity) is actors.Hero:
                        return pos
                    elif entity != self.map.WALKABLE:
                        # something blocks @self's view
                        return None
                return None

            for direction in ('up', 'down', 'left', 'right'):
                pos = try_direction(direction)
                if pos is not None:
                    return pos, direction

            return None, None

        def move_to_last_seen():
            if enemy.last_seen is None:
                return

            if enemy.pos == enemy.last_seen:
                enemy.last_seen = None
                enemy.hero_direction = None
                return

            self.move_actor(enemy, enemy.hero_direction)
        
        def hero_is_in_vicinity():
            # Returns True if hero is directly above, below, to the right
            # or to the left of @enemy.
            pos_row, pos_col = enemy.pos
            hero_row, hero_col = hero_pos
            return abs(pos_row - hero_row) <= 1 and abs(pos_col - hero_col) <= 1

        def attack_hero():
            # Call only when the hero is next to @enemy!
            # The enemy determines the attack type dealing the most
            # damage and inflicts it on the hero.
            # TODO: make the enemy smarter
            self.actor_attack(enemy, 'fist', enemy.hero_direction)
        
        hero_pos, hero_direction = search_for_hero()
        if hero_pos is None:
            # the enemy cannot see the hero
            move_to_last_seen()
        else:
            enemy.last_seen = hero_pos
            enemy.hero_direction = hero_direction
            if hero_is_in_vicinity():
                attack_hero()
            else:
                move_to_last_seen()

    def reset(self):
        # resets the state of @self to what it was at the beginning
        cpy = copy.deepcopy(self.initial_state)
        self.__dict__.update(cpy)

    def display(self):
        def display_hero():
            print(f'health: {self.hero.health}')
            print(f'mana: {self.hero.mana}')
            print(f'weapon: {self.hero.weapon.name}')
            print(f'spell: {self.hero.spell.name}')
            print()

        def display_map():
            lines = (''.join(line) for line in self.map_chars)
            print('\n'.join(lines))
            print()
        
        os.system('clear')
        display_hero()
        display_map()

    def refresh_display(self):
        self.map_chars = self.map.chars
        self.display()
        
    def play(self):
        while True:
            self.refresh_display()
            
            try:
                self.hero_turn()
            except KeyboardInterrupt:
                command = input('>>> ')
                if command == 'q':
                    return self.QUIT
                elif command == 'r':
                    self.reset()
                    continue
                else:
                    # unknown command
                    continue

            self.refresh_display()
                
            if self.hero.pos == self.map.gateway_pos:
                return self.WON
            
            # after the hero's turn, some enemies may be dead, so stop tracking them
            self.enemies = [enemy for enemy in self.enemies if enemy.is_alive]
            
            for enemy in self.enemies:
                self.enemy_turn(enemy)
                
            # after the enemies' turn, the hero may have died
            if not self.hero.is_alive:
                return self.KILLED

class Dungeon:
    # attributes:
    #  - hero_partial_dict
    #  - enemies_data: used to create the enemy_partial_dicts iterator
    #  - map_template
    #  - treasures
    
    @staticmethod
    def from_file(path):
        with open(path) as f:
            text = f.read()
        return Dungeon.from_dict(json.loads(text))
    
    @staticmethod
    def from_dict(dct):
        result = Dungeon.__new__(Dungeon)
        result.hero_partial_dict = dct['hero']
        result.enemy_data = dct['enemies']
        result.map_template = dct['map_template']
        result.treasures = [treasures.parse_dict(tdict) for tdict in dct['treasures']]
        return result

    @property
    def spawn_posns(self):
        # returns an iterator of @self's spawn positions        
        nrows = len(self.map_template)
        ncols = len(self.map_template[0])
        for rowi in range(nrows):
            for coli in range(ncols):
                if self.map_template[rowi][coli] == 'S':
                    yield (rowi, coli)
        
    def games(self):
        return (self.create_game(spawn_pos) for spawn_pos in self.spawn_posns)

    @property
    def enemy_partial_dicts(self):        
        if type(self.enemy_data) is list:
            return iter(self.enemy_data)
        return itertools.repeat(self.enemy_data['all'])
    
    def create_game(self, spawn_pos):
        # @spawn_location must be one of @self's spawn locations.
        # Returns the Game instance with the hero at @spawn_location.

        enemy_partial_dicts = self.enemy_partial_dicts
        hero = None
        enemies = []
        the_map = Map([list(row) for row in self.map_template])
        for pos in the_map.posns_lrtb:
            char = the_map[pos]
            if char == 'S':
                if pos == spawn_pos:
                    hero_dict = copy.deepcopy(self.hero_partial_dict)
                    hero_dict['pos'] = pos
                    hero = actors.Hero.from_dict(hero_dict)
                    the_map[pos] = hero
                else:
                    the_map[pos] = Map.WALKABLE
            elif char == 'T':
                chest = treasures.TreasureChest(pos, self.treasures)
                the_map[pos] = chest
            elif char == 'E':
                enemy_dict = next(enemy_partial_dicts)
                enemy_dict['pos'] = pos
                enemy = actors.Enemy.from_dict(enemy_dict)
                enemies.append(enemy)
                the_map[pos] = enemy
            elif char == 'G':
                the_map.gateway_pos = pos
                the_map[pos] = Map.GATEWAY
            elif char == '#':
                the_map[pos] = Map.OBSTACLE
            elif char == '.':
                the_map[pos] = Map.WALKABLE
            else:
                raise ValueError(f'invalid character in map template: "{char}"')
        return Game(hero, enemies, the_map)
