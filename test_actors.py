import unittest
from actors import *
import treasures
from treasures import Weapon
from treasures import Spell
from dungeon import Map

class TestHero(unittest.TestCase):
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

		
		
	def test_if_created_object_from_class_is_Hero(self):
		self.assertIsInstance(self.hero, Hero)
		self.assertEqual(self.hero.name, "Bron")
		self.assertEqual(self.hero.title, "dragon slayer")
		self.assertEqual(self.hero.health, 100)
		self.assertEqual(self.hero.mana, 100)
		self.assertEqual(self.hero.mana_regeneration_rate, 2)

	def test_known_as(self):
		self.assertEqual(self.hero.known_as, "Bron the dragon slayer")

	def test_if_hero_is_alive(self):
		self.assertEqual(self.hero.is_alive, True)

	def test_if_hero_can_cast(self):
		self.assertEqual(self.hero.can_cast, True)

	def test_when_hero_is_damaged(self):
		self.hero.damage(20)
		self.assertEqual(self.hero.health, 80)

	def test_when_hero_is_healed(self):
		self.hero.damage(20)
		self.hero.heal(10)
		self.assertEqual(self.hero.health, 90)

	def test_when_is_taken_mana(self):
		self.hero.take_mana(15)
		self.assertEqual(self.hero.mana, 85)

	def test_when_is_given_mana(self):
		self.hero.take_mana(15)
		self.hero.give_mana(10)
		self.assertEqual(self.hero.mana, 95)

	def test_when_the_hero_is_equiped(self):
		self.hero.equip(self.hero.weapon)

	def test_when_hero_learns_new_spell(self):
		self.hero.learn(self.hero.spell)

	def test_when_hero_makes_move_by_given_direction(self):
		self.hero.move("right")
		self.assertEqual(self.hero.pos, (0,1))

	def test_when_hero_attack_by_given_direction(self):
		self.assertEqual(self.hero.attack("spell","right"), None)
		

class TestEnemy(unittest.TestCase):
	def setUp(self):
		self.dct = {
         "health":100, 
         "mana":100,
         "fist_damage":20,
         "pos":(2,5),
    
      "map":Map([
         ["S",".","#","#",".",".","S",".",".","T"],
         ["#","T","#","#","S",".","#","#","#","."],
         ["#",".","#","#","#","E","#","#","#","E"],
         ["#",".","E",".",".",".","#","#","#","."],
         ["#","#","#","T","#","#","#","#","#","G"]])
 
     }



		self.enemy = Enemy.from_dict(self.dct)

		
		
	def test_if_created_object_from_class_is_Enemy(self):
		self.assertIsInstance(self.enemy, Enemy)
		self.assertEqual(self.enemy.health, 100)
		self.assertEqual(self.enemy.mana, 100)
		self.assertEqual(self.enemy.fist_damage, 20)

	def test_if_enemy_is_alive(self):
		self.assertEqual(self.enemy.is_alive, True)

	def test_if_enemy_can_cast(self):
		self.assertEqual(self.enemy.can_cast, True)

	def test_when_enemy_is_damaged(self):
		self.enemy.damage(20)
		self.assertEqual(self.enemy.health, 80)

	def test_when_enemy_is_healed(self):
		self.enemy.damage(20)
		self.enemy.heal(10)
		self.assertEqual(self.enemy.health, 90)

	def test_when_is_taken_mana_ffrom_enemy(self):
		self.enemy.take_mana(15)
		self.assertEqual(self.enemy.mana, 85)

	def test_when_is_given_mana_to_enemy(self):
		self.enemy.take_mana(15)
		self.enemy.give_mana(10)
		self.assertEqual(self.enemy.mana, 95)

	def test_when_the_enemy_is_equiped(self):
		self.enemy.equip(self.enemy.weapon)

	def test_when_enemy_learns_new_spell(self):
		self.enemy.learn(self.enemy.spell)

	def test_returns_the_position_of_hero_when_enemy_searches_for_hero(self):
		self.assertEqual(self.enemy.search_for_hero(),(None, None))

	def test_returns_the_position_of_hero_when_enemy_searches_for_hero(self):
		self.enemy.move_to_last_seen()
		self.assertEqual(self.enemy.pos,(2,5))

	def test_if_hero_is_in_vicinity(self):
		self.enemy.pos = (0,1)
		self.assertEqual(self.enemy.do_turn(),None)



if __name__ == '__main__':
	unittest.main()
