import unittest
from dungeon import *
from actors import *
class TestDungeon(unittest.TestCase):
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
		self.dct1 = {
			 "health":100, 
			 "mana":100,
			 "fist_damage":20,
			 "pos":(2,5),
		
		  "map":self.hero.map
		  
	 
		}
		self.enemy = Enemy.from_dict(self.dct1)
		self.g = Game(self.hero, self.enemy, self.hero.map)

		self.dict_data = {
      "hero":{
         "name":"Bron",
         "title":"dragon slayer",
         "health":100, "mana":100,
         "mana_regeneration_rate":2
      },
      "enemies":[
         {
            "health":100,
            "mana":100,
            "fist_damage":20
         },
         {
            "health":100,
            "mana":100,
            "fist_damage":30
         },
         {
            "health":100,
            "mana":100,
            "fist_damage":25         }
      ],      
      "map_template":[
         "S.##..S..T",
         "#T##S.###.",
         "#.###E###E",
         "#.E...###.",
         "###T#####G"
      ],
      "treasures":[
         {
            "type":"weapon",
            "name":"The Axe of Destiny",
            "damage":20
         },
         {
            "type":"spell",
            "name":"Fireball",
            "damage":30,
            "mana_cost":50,
            "cast_range":2
         },
         {
            "type":"health_potion",
            "amount":10
         },
         
         {
            "type":"mana_potion",
            "amount":10
         },
         
      ]
   }
		

		self.d = Dungeon.from_dict(self.dict_data)
		self.spawn_positions = []
		for pos in self.d.spawn_posns:
			self.spawn_positions.append(pos)

	def test_if_map_initialization_is_correct(self):
		for i in range(self.hero.map.nrows):
			for j in range(self.hero.map.ncols):
				self.assertIn(self.hero.map[i,j],["S","H","T","E","G",".","#"])
				self.assertEqual(len(self.hero.map[i,j]),1)

	def test_when_returns_number_of_rows_of_a_matrix(self):
		self.assertEqual(self.hero.map.nrows, 5)

	def test_when_returns_number_of_cols_of_a_matrix(self):
		self.assertEqual(self.hero.map.ncols, 10)

	def test_when_returns_matrix_after_cleanup(self):
		self.hero.map.cleanup_at((1,1))
		self.assertEqual(self.hero.map[1,1], '.')

	def test_when_returns_True_when_pos_is_valid(self):
		self.assertEqual(self.hero.map.pos_is_valid([1,1]), True)
		self.assertEqual(self.hero.map.pos_is_valid([10,1]), False)

	def test_when_returns_True_when_hero_can_move_to_pos(self):
		self.assertEqual(self.hero.map.can_move_to([0,1]), True)
		self.assertEqual(self.hero.map.can_move_to([10,1]), False)


	def test_when_return_positions_to_move_by_given_direction(self):
		pos = self.hero.map.positions([0,0], 'up')
		res = []
		for el in pos:
			res.append(el)
		self.assertEqual(res, [])
		pos = self.hero.map.positions([0,0], 'down')
		res = []
		for el in pos:
			res.append(el)
		self.assertEqual(res, [(1, 0), (2, 0), (3, 0), (4, 0)])
		pos = self.hero.map.positions([0,0], 'left')
		res = []
		for el in pos:
			res.append(el)
		self.assertEqual(res, [])
		pos = self.hero.map.positions([0,0], 'right')
		res = []
		for el in pos:
			res.append(el)
		self.assertEqual(res, [(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (0, 8), (0, 9)])

	def test_when_return_iteral_of_the_positions(self):
		self.assertEqual(str(type(self.hero.map.posns_lrtb)),"<class 'generator'>")

	def test_when_return_all_neighbours_of_element_by_given_position(self):
		a = self.hero.map.neighbours([0,0])
		result = []
		for el in a:
			result.append(el)
		self.assertEqual(result,[(0, 1),(1, 0),(1, 1)])

	def test_if_game_initialization_is_correct(self):
		self.assertIsInstance(self.hero, Hero)
		self.assertIsInstance(self.enemy, Enemy)
		self.assertIsInstance(self.hero.map, Map)
		self.assertIsInstance(self.g, Game)

	def test_if_reading_is_correct(self):
		filename = "dict_data.json"
		self.assertIsInstance(Dungeon.from_dict(self.dict_data), Dungeon)

	def test_when_returns_list_of_spawn_positions(self):
		result = []
		for pos in self.d.spawn_posns:
			result.append(pos)
		self.assertEqual(result,[(0, 0), (0, 6), (1, 4)])

	def test_if_returns_generator_of_games(self):
		self.assertEqual(str(type(self.d.games())),"<class 'generator'>")

	def test_if_returns_iterator_of_enemie(self):
		self.assertEqual(str(type(self.d.enemy_partial_dicts)),"<class 'list_iterator'>")

	def test_if_returns_list_of_enemies(self):
		result = []
		for enemy in self.d.enemy_partial_dicts:
			result.append(enemy)
		self.assertEqual(result,[{'health': 100, 'mana': 100, 'fist_damage': 20},
								{'health': 100, 'mana': 100, 'fist_damage': 30},
								{'health': 100, 'mana': 100, 'fist_damage': 25}])

	def test_if_creates_game(self):
		self.d.create_game(self.spawn_positions)
		self.assertEqual(type(self.d.create_game(self.spawn_positions)),Game)

if __name__ == '__main__':
	unittest.main()
