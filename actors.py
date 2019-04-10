import utils
from treasure import TreasureChest

class Actor:
    # base class for Enemy and Hero
    # all instances of Actor should provide the following attributes:
    # - health
    # - max_health
    # - mana
    # - max_mana
    # - map
    # - weapon
    #     all actors have a weapon. by default it is weapon.plastic_sword,
    #     which inflicts no damage.
    # - spell
    #     all actors have a spell. by default it is spell.TODO
    # - pos: a valid position within map
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
        
    def do_turn(self):
        # called when it is the actor's turn
        raise NotImplementedError

    def accept_treasure(self, treasure):
        # each actor can decide if he will accept the @treasure.
        raise NotImplementedError
    
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
        
        raise NotImplementedError
        
            


class Hero(Actor):
    # a Hero has the following additional attributes:
    # - name
    # - title
    # important invariant: a Hero's fist_damage will always be 0
    
    @property
    def known_as(self):
        return f"{self.name} the {self.title}"

    def read_command(self):
        # returns one of:
        # {'up', 'down', 'left', 'right',
        #  ('weapon', 'up'), ..., ('weapon', 'right'),
        #  ('spell', 'up', ...', ('spell', 'right')}
        # THIS FUNCTION DETERMINES THE USER CONTROL KEYS
        raise NotImplementedError
        
        
    def do_turn(self):
        command = self.read_command()
        if type(command) is str:
            # command is one of {'up', 'down', 'left', 'right'}
            self.move(command)
        else:
            # command is one of:
            # {('weapon', 'up'), ..., ('weapon', 'right'),
            #  ('spell', 'up', ...', ('spell', 'right')}}
            self.attack(*command)
            
class Enemy(Actor):
    # additional attributes:
    #  - last_seen: the position the hero was last seen in.
    #  - hero_direction: always equal to utils.relative_direction(self.pos, self.last_seen);
    #                    it is included only for convenience.
    #  if the enemy does not know where the hero is, self.last_seen and
    #  self.hero_direction will both be None.

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

            if self.weapon.damage > self.fist_damage:
                if self.mana >= self.spell.
                by = 'weapon' if self.weapon.damage >= self.spell.damage else 'spell'
            else:
                by = 'fist' if self.fist_damage >= self.spell.damage else 'spell'

            self.attack(by, self.hero_direction)
        
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
