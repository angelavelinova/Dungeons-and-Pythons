import json
from weapon import Weapon
from spell import Spell

# ========================================
# constants

SPAWN = 'S'
GATEWAY = 'G'
WALKABLE = '.'
TREASURE = 'T'
OBSTACLE = '#'
ENEMY = 'E'
HERO = 'H'

# ========================================

class Map:
    def __init__(self, matrix):
        self.matrix = matrix
    
    @property
    def nrows(self):
        # returns the number of rows in @self
        pass

    @property
    def ncols(self):
        # returns the number of columns in @self
        raise NotImplementedError

    def cleanup_at(self, pos):
        # responsible for removing dead bodies and looted treasures
        raise NotImplementedError

    def contains_treasure_at(self, pos):
        # returns True iff self[pos] is a treasure chest
        raise NotImplementedError
    
    def can_move_to(self, pos):
        # returns True if pos is within @self and if there is nothing
        # at that position that prevents you from moving there.
        raise NotImplementedError
    
    @property
    def gateway_pos(self):
        # returns the coordinates (<row-index>, <col-index>) of the gateway
        raise NotImplementedError

    def display(self):
        raise NotImplementedError

    def remove_actor(self, actor_pos):
        # @actor_pos must be a valid position within @self
        # removes the actor at the position @actor_pos.
        # if @actor_pos does not point to an actor, a ValueError is raised
        pass

    def __getitem__(self, pos):
        # pos must be a pair (<row-index>, <column-index>)
        row, col = pos
        return self.matrix[row][col]

    def __setitem__(self, pos, value):
        # pos must be a pair (<row-index>, <column-index>)
        row, col = pos
        self.matrix[row][col] = value
    
    def positions(self, pos, direction):
        # direction must be one in {'up', 'down', 'left', 'right'}.
        # returns an iterator of positions relative to @pos.
        raise NotImplementedError

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
    #  - hero_dict
    #  - enemy_dicts
    #  - map_template
    #  - treasures
    
    @staticmethod
    def from_file(path):
        with open(path) as f:
            text = f.read()
        return Dungeon.from_dict(json.loads(text))
    
    @staticmethod
    def from_dict(d):
        result = Dungeon.__new__(Dungeon)
        result.hero_dict = d['hero']
        result.enemy_dicts = d['enemies']
        result.map_template = d['map']

        treasures = []
        for treasure_dict in dict['treasures']:
            treasure_type = treasure_dict['type']
            if treasure_type == 'weapon':
                name, damage = treasure_dict['name'], treasure_dict['damage']
                treasures.append(Treasure(name, damage))
            elif treasure_type == 'spell':
                name, damage, mana_cost, cast_range = [treasure_dict[attr]
                                                       for attr in ('name', 'damage', 'mana_cost', 'cast_range')]
                treasures.append(Spell(name, damage, mana_cost, cast_range))
            elif treasure_type == 'health':
                treasures.append(potions.HealthPotion(treasure_dict['amount']))
            elif treasure_type == 'mana':
                treasures.append(potions.ManaPotion(treasure_dict['amount']))
        
        result.treasures = treasures
        return result
        
    def create_game(self, spawn_location):
        # @spawn_location must be one of @self's spawn locations.
        # Returns the Game instance with the hero at @spawn_location.
        # remember to set the hero and enemies map and pos
        
        def make_map():
            result = [list(row) for row in self.map_template]
            nrows = len(result)
            ncols = len(result[0])
            for rowi in range(nrows):
                for coli in range(ncols):
                    char = result[rowi][coli]
                    if char == 'S':
                        if (rowi, coli) == spawn_location:
                            result[rowi][coli] = hero
                            hero.pos = (rowi, coli)
                        

        hero = Hero.from_dict(self.hero_dict)
        enemies = [Enemy.from_dict(enemy_dict) for enemy_dict in self.enemy_dicts]
        game_map = make_map()
        # set hero and enemies' maps to game_map
        return Game(hero, enemies, game_map)
        
