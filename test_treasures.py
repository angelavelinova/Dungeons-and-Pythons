import unittest
from treasures import *
from dungeon import *
from actors import *
class TestTreasures(unittest.TestCase):
	def setUp(self):
		self.dct = {
		"name":"Bron",
		"title":"dragon slayer",
		"health":100, "mana":100,
		"mana_regeneration_rate":2,
		"fist_damage":2,
		"pos":(0,0),
	
		"map":Map([
		["H",".","#","#",".",".","S",".",".","T"],
		["#","T","#","#","S",".","#","#","#","."],
		["#",".","#","#","#","E","#","#","#","E"],
		["#",".","E",".",".",".","#","#","#","."],
		["#","#","#","T","#","#","#","#","#","G"]])
	  
 
		}
		self.hero = Hero.from_dict(self.dct)
		self.dict_treasures = {
        0: {
            "type":"weapon",
            "name":"The Axe of Destiny",
            "damage":20
         },
        1: {
            "type":"spell",
            "name":"Fireball",
            "damage":30,
            "mana_cost":50,
            "cast_range":2
         },
        2: {
            "type":"health_potion",
            "amount":10
         },
        3: {
            "type":"mana_potion",
            "amount":10
         },

      }
		self.obj = TreasureChest((0,0), self.dct["map"], [(1,1), (0,9),(4,3)])

		self.treasures = []
		for key in self.dict_treasures: 
			self.treasures.append(parse_dict(self.dict_treasures[key]))
	
	def test_when_object_from_class_TreasureChest_is_valid(self):
		self.assertEqual(isinstance(self.obj, TreasureChest), True)
		self.assertEqual(self.obj.pos, (0,0))
		self.assertEqual(self.obj.map, self.dct["map"])
		self.assertEqual(self.obj.treasures, [(1,1), (0,9),(4,3)])

	def test_when_treasure_is_opened(self):
		self.assertIn(self.obj.open(), [(1,1), (0,9),(4,3)])

	def test_when_read_treasures_from_dictionary(self):
		for key in self.dict_treasures:
			self.assertIn(type(parse_dict(self.dict_treasures[key])), [Weapon, Spell, HealthPotion, ManaPotion])

	def test_class_HealthPotion(self):
		for treasure in self.treasures:
			if type(treasure) == HealthPotion:
				self.assertEqual(treasure.amount, 10)

			if type(treasure) == ManaPotion:
				self.assertEqual(treasure.amount, 10)

			if type(treasure) == Weapon:
				self.assertEqual(treasure.name, "The Axe of Destiny")
				self.assertEqual(treasure.damage, 20)

			if type(treasure) == Spell:
				self.assertEqual(treasure.name, "Fireball")
				self.assertEqual(treasure.damage, 30)
				self.assertEqual(treasure.mana_cost, 50)
				self.assertEqual(treasure.cast_range,2)

	
if __name__ == '__main__':
	unittest.main()
