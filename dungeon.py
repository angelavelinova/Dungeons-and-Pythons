from treasure_chest import TreasureChest
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
    def __init__(self, matrix, gateway_pos):
        self.matrix = matrix
        self.gateway_pos = gateway_pos

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
        return isistance(self[pos], TreasureChest)
    
    def can_move_to(self, pos):
        # returns True if pos is within @self and if there is nothing
        # at that position that prevents you from moving there.
        row, col = pos
        if row >= 0 and row <= self.nrows and col >= 0 and col <= self.cols:
            if isinstance(self[pos], TreasureChest) or self[pos] == "." or self[pos] == "G":
                return True
        return False

    def display(self):
        for row in range(self.nrows):
            lst = []
            for col in range(self.ncols):
                if  isinstance(self[row,col], TreasureChest):
                    lst.append('T')
                elif isinstance(self[row,col], Hero):
                    lst.append('H')
                elif isinstance(self[row,col], Enemy):
                    lst.append('E')
                else:
                    lst.append(self[row,col])
            ''.join(lst)
            print(lst)

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

