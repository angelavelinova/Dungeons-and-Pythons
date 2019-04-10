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
    @property
    def nrows(self):
        # returns the number of rows in @self
        raise NotImplementedError

    @property
    def ncols(self):
        # returns the number of columns in @self
        raise NotImplementedError

    def cleanup_at(self, pos):
        # responsible for removing dead bodies and looted treasures
        raise NotImplementedError

    def contains_treasure_at(self, pos):
        # returns True iff self[pos] is a treasure
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
        raise NotImplementedError

    def __setitem__(self, pos, value):
        # pos must be a pair (<row-index>, <column-index>)
        # 
        raise NotImplementedError
    
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
    @classmethod
    def from_file(cls, path):
        # Returns the Dungeon corresponding to the text of the file at @path.
        raise NotImplementedError

    def create_game(self, spawn_location):
        # @spawn_location must be one of @self's spawn locations.
        # Returns the Game instance with the hero at @spawn_location.
        raise NotImplementedError

