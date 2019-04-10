import json
import copy
import treasure
from weapon import Weapon
from spell import Spell

class Map:
    def __init__(self, matrix):
        self.matrix = matrix
                
    @property
    def nrows(self):
        return len(self.matrix)

    @property
    def ncols(self):
        return len(self.matrix[0])

    def cleanup_at(self, pos):
        self[pos] = "."
        
    def contains_treasure_at(self, pos):
        # returns True iff self[pos] is a treasure
        return isinstance(self[pos], treasure.TreasureChest)
    
    def can_move_to(self, pos):
        # returns True if pos is within @self and if there is nothing
        # at that position that prevents you from moving there.
        row, col = pos
        if row >= 0 and row <= self.nrows and col >= 0 and col <= self.cols:
            if isinstance(self[pos], treasure.TreasureChest) or self[pos] == "." or self[pos] == "G":
                return True
        return False

    def display(self):
        for row in range(self.nrows):
            lst = []
            for col in range(self.ncols):
                if  isinstance(self[row,col], treasure.TreasureChest):
                    lst.append('T')
                elif isinstance(self[row,col], Hero):
                    lst.append('H')
                elif isinstance(self[row,col], Enemy):
                    lst.append('E')
                else:
                    lst.append(self[row,col])
            print(''.join(lst))

    def remove_actor(self, actor_pos):
        # @actor_pos must be a valid position within @self
        # removes the actor at the position @actor_pos.
        # if @actor_pos does not point to an actor, a ValueError is raised
        if isinstance(self[actor_pos], Hero):
            self[actor_pos] = '.'
        else: 
            raise ValueError

    def __getitem__(self, pos):
        # pos must be a pair (<row-index>, <column-index>)
        row, col = pos
        return self.matrix[row][col]

    def __setitem__(self, pos, value):
        # pos must be a pair (<row-index>, <column-index>)
        row, col = pos
        self.matrix[row][col] = value
    
    def positions(self, pos, direction):
        row, col = pos
        res = []
        if direction == 'up':
            row -= 1
            while row >= 0:
                res.append((row,col))
                row -= 1

        elif direction == 'down':
            row += 1
            while row < self.nrows:
                res.append((row,col))
                row += 1

        elif direction == 'left':
            col -= 1
            while col >= 0:
                res.append((row,col))
                col -= 1

        elif direction == 'right':
            col += 1
            while col < self.ncols:
                res.append((row,col))
                col += 1

        return res

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

    def __init__(self, hero, enemies, map):
        # @hero should be a Hero instance whose map is @map
        # @enemies should be a list of Enemy instances and each enemy's map should be @map
        # @map should be a Map instance
        
        self.hero = hero
        self.enemies = enemies
        self.map = map
    
    def play(self):
        while True:
            self.map.display()
            self.hero.do_turn()
            if hero.pos == self.map.gateway_pos:
                return Game.WON
            # after the hero's turn, some enemies may be dead, so stop tracking them
            self.enemies = [enemy for enemy in self.enemies if enemy.is_alive]
            for enemy in self.enemies:
                enemy.do_turn()
            # after the enemies' turn, the hero may have died
            if not hero.is_alive:
                return Game.KILLED

class Dungeon:
    # attributes:
    #  - hero_partial_dict
    #  - enemy_partial_dicts
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
        result.enemies_partial_dicts = dct['enemies']
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
            
    def create_game(self, spawn_pos):
        # @spawn_location must be one of @self's spawn locations.
        # Returns the Game instance with the hero at @spawn_location.
        
        enemy_partial_dicts = iter(self.enemy_partial_dicts)
        hero = None
        enemies = []
        the_map = Map([list(row) for row in self.map_template])
        for pos in self.posns_lrtb:
            char = the_map[pos]
            if char == 'S':
                if pos == spawn_pos:
                    hero_dict = copy.deepcopy(self.hero_partial_dict)
                    hero_dict['map'] = the_map
                    hero_dict['pos'] = pos
                    hero = Hero.from_dict(hero_dict)
                    the_map[pos] = hero
                else:
                    the_map[pos] = '.'
            elif char == 'T':
                chest = treasure.TreasureChest(pos, the_map, self.treasures)
                the_map[pos] = chest
            elif char == 'E':
                enemy_dict = next(enemy_partial_dicts)
                enemy_dict['pos'] = pos
                enemy_dict['map'] = the_map
                enemy = Enemy.from_dict(enemy_dict)
                enemies.append(enemy)
                the_map[pos] = enemy
            elif char == 'G':
                the_map.gateway_pos = pos                 
                        
        return Game(hero, enemies, the_map)
