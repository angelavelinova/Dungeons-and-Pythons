import utils
import treasures

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
    
    def take_healing(self, healing_points):
        if not self.is_alive:
            raise ValueError('cannot heal a dead actor')
        else:
            self.health = min(self.max_health, self.health + healing_points)
            return True
        
    def take_mana(self, mana_points):
        self.mana = min(self.max_mana, self.mana + mana_points)

    def take_damage(self, damage_points):
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

    def accept_treasure(self, the_treasure):
        if type(the_treasure) is treasure.Weapon:
            self.equip(the_treasure)
        elif type(the_treasure) is treasure.Spell:
            self.learn(the_treasure)
        elif type(the_treasure) is treasure.HealthPotion:
            self.take_healing(the_treasure.amount)
        elif type(the_treasure) is treasure.ManaPotion:
            self.take_mana(the_treasure.amount)
        else:
            raise TypeError(f'invalid treasure type: {type(the_treasure)}')
    
    def move(self, direction):
        # @direction must be one of {'up', 'down', 'left', 'right'}
        # if it is possible to move the actor in @direction, moves him and returns True;
        # otherwise, return False
    
        new_pos = utils.move_pos(self.pos, direction)
        
        if not self.map.can_move_to(new_pos):
            return False

        if self.map.contains_treasure_at(new_pos):
            self.accept_treasure(self.map[new_pos].open())

        # at this point self.map[pos] contains a walkable.
        # swap the walkable with self
        self.map[self.pos], self.map[new_pos] = self.map[new_pos], self.map[self.pos]
        self.pos = new_pos

    def attack(self, by, direction):
        # @by must be in {'weapon', 'spell', 'fist'}
        # @direction must be in {'up', 'down', 'left', 'right'}

        nemesis_pos = utils.move_position(self.pos, direction)
        nemesis = self.map[nemesis_pos]

        if by == 'weapon':
            nemesis.take_damage(self.weapon.damage)
        elif by == 'spell':
            if self.mana >= self.spell.mana_cost:
                nemesis.take_damage(self.spell.damage)
            else:
                raise ValueError('not enough mana')
        else:
            nemesis.take_damage(self.fist_damage)
                            
class Hero(Actor):
    # a Hero has the following additional attributes:
    # - name
    # - title

    @staticmethod
    def from_dict(dct):
        # the dict must have the keys
        # {'name', 'title', 'health', 'mana', 'fist_damage', 'map', 'pos'}
        result = object.__new__(Enemy)
        self.name = dct['name']
        self.title = dct['title']
        self.health = self.max_health = dct['health']
        self.mana = self.max_mana = dct['mana']
        self.fist_damage = dct['fist_damage']
        self.pos = dct['pos']
        self.map = dct['map']
        self.weapon = treasures.Weapon()
        self.spell = treasures.Spell()
    
    @property
    def known_as(self):
        return f"{self.name} the {self.title}"

    def read_command(self):
        # returns one of:
        # {'up', 'down', 'left', 'right',
        #  ('weapon', 'up'), ..., ('weapon', 'right'),
        #  ('fist', 'up'), ..., ('fist', 'right'),
        #  ('spell', 'up', ...', ('spell', 'right')}
        # TODO: handle user chars better
        # THIS FUNCTION DETERMINES THE USER CONTROL KEYS
        
        first_char = utils.get_char()
        if first_char in '2468':
            return {'2': 'down', '4': 'left', '6': 'right', '8': 'up'}[first_char]
        elif first_char in 'wsf':
            by = {'w': 'weapon', 's': 'spell', 'f': fist}[first_char]
            second_char = utils.get_char()
            if second_char not in '2468':
                raise ValueError(f'invalid second character: "{second_char}". expected one of "2468"')
            direction = {'2': 'down', '4': 'left', '6': 'right', '8': 'up'}[second_char]
            return by, direction
        else:
            raise ValueError(f'invalid first char: "{first_char}". expected one of "2468wsf"')
                
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
        self.health = self.max_health = dct['health']
        self.mana = self.max_mana = dct['mana']
        self.fist_damage = dct['fist_damage']
        self.pos = dct['pos']
        self.map = dct['map']
        self.weapon = treasures.Weapon()
        self.spell = treasures.Spell()
        
    def search_for_hero(self):
        # returns the position of the hero, or None if he can't be seen
        # @self will only look up, down, left and right

        def try_positions(positions):
            # returns the position which contains Hero
            # or None if there is no such position in @positions
            return next((pos for pos in positions if type(self.map[pos]) is Hero), None)

        return next((pos in map(try_positions,
                                (self.map.positions(self.pos, direction)
                                 for direction in ('up', 'down', 'left', 'right')))
                     if pos is not None),
                    None) # next default return value

    def move_to_last_seen(self):
        if self.last_seen is None:
            return

        if self.pos == self.last_seen:
            self.last_seen = None
            self.hero_direction = None
            return

        self.move(self.hero_direction)
    
    def do_turn(self):
        def hero_in_vicinity():
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
        
        hero_pos = self.search_for_hero()
        if hero_pos is None:
            # the enemy cannot see the hero
            self.move_to_last_seen()
        else:
            if hero_in_vicinity():
                attack_hero()
            else:
                self.last_seen = hero_pos
                self.hero_direction = utils.relative_direction(self.pos, hero_pos)
                self.move_to_last_seen()
