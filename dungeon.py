import json
import copy
import treasures
import actors
import os
import itertools
import utils

class Map:
    WALKABLE = ' '
    ENEMY = '+'
    GATEWAY = 'O'
    TREASURE_CHEST = 'T'
    HERO = 'X'
    OBSTACLE = '#'
    NORTH_BORDER = '.'
    SOUTH_BORDER = '.'
    WEST_BORDER = '.'
    EAST_BORDER = '.'
    
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

    def display(self):
        print(' ' + self.NORTH_BORDER * self.ncols)
        for row in range(self.nrows):
            lst = [self.WEST_BORDER]
            for col in range(self.ncols):
                if isinstance(self[row,col], treasures.TreasureChest):
                    lst.append(self.TREASURE_CHEST)
                elif isinstance(self[row,col], actors.Hero):
                    lst.append(self.HERO)
                elif isinstance(self[row,col], actors.Enemy):
                    lst.append(self.ENEMY)
                else:
                    lst.append(self[row,col])
            lst.append(self.EAST_BORDER)
            print(''.join(lst))
        print(' ' + self.SOUTH_BORDER * self.ncols)
        print()

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
                      (r+1, c), (r+1, c), (r+1, c+1))
        
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

        # needed for restarting the game
        self.initial_state = copy.deepcopy(self.__dict__)

    def reset_state(self):
        cpy = copy.deepcopy(self.initial_state)
        self.__dict__.update(cpy)
        
    def play(self):
        def display():
            os.system('clear')
            self.hero.display()
            self.map.display()
        
        while True:
            display()
            
            try:
                self.hero.do_turn()
            except KeyboardInterrupt:
                command = input('>>> ')
                if command == 'q':
                    return self.QUIT
                elif command == 'r':
                    self.reset_state()
                    continue
                else:
                    # unknown command
                    continue

            display()
                
            if self.hero.pos == self.map.gateway_pos:
                return self.WON
            
            # after the hero's turn, some enemies may be dead, so stop tracking them
            self.enemies = [enemy for enemy in self.enemies if enemy.is_alive]
            
            for enemy in self.enemies:
                enemy.do_turn()
                
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
                    hero_dict['map'] = the_map
                    hero_dict['pos'] = pos
                    hero = actors.Hero.from_dict(hero_dict)
                    the_map[pos] = hero
                else:
                    the_map[pos] = Map.WALKABLE
            elif char == 'T':
                chest = treasures.TreasureChest(pos, the_map, self.treasures)
                the_map[pos] = chest
            elif char == 'E':
                enemy_dict = next(enemy_partial_dicts)
                enemy_dict['pos'] = pos
                enemy_dict['map'] = the_map
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
