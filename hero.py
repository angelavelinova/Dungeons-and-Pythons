class Hero:
    def __init__(self, name, title, health, mana, mana_regeneration_rate):
        self.name = name
        self.title = title
        self.health = health
        self.mana = mana
        self.max_mana = mana
        self.mana_regeneration_rate = mana_regeneration_rate
        self.max_health = health

    @property
    def known_as(self):
        return f"{self.name} the {self.title}"

    @property
    def health(self):
        return self.health

    @property
    def is_alive(self):
        return self.health != 0

    @property
    def can_cast(self):
        return self.mana != 0
    
    def take_damage(self, damage_points):
        self.health = max(0, self.health - damage_points)

    def take_healing(self, healing_points):
        if not self.is_alive:
            return False
        else:
            self.health = min(self.max_health, self.health + healing_points)
            return True
        
    def take_mana(self, mana_points):
        self.mana = min(self.max_mana, self.mana + mana_points)


    def get_user_input(self):
        # returns one of:
        # {'up', 'down', 'left', 'right',
        #  ('weapon', 'up') ... ('weapon', 'right'),
        #  ('spell', up'), ..., ('spell', 'right')}
        # based on the user input
        pass
        
    def turn(self, handle):
        command = self.get_user_input()
        if type(command) is str:
            # command is one of {'up', 'down', 'left', 'right'}
            handle.move(command)
        else:
            # command is one of
            # {('weapon', 'up') ... ('weapon', 'right'),
            #  ('spell', up'), ..., ('spell', 'right')}
            kind, direction = command
            if kind is 'weapon':
                raise NotImplementedError
            else:
                raise NotImplementedError
