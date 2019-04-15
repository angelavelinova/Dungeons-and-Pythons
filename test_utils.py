import unittest
from utils import *
class TestUtils(unittest.TestCase):

	#def test_when_gets_char_from_terminal(self):
	#	a = get_char()
	#	expected_result = True
	#	self.assertEqual(isinstance(a, str),expected_result)

	def test_when_returns_the_direction_in_which_one_would_have_to_go_from_pos1_to_get_to_pos2(self):
		self.assertEqual(relative_direction((0,0), (0,2)),'right')
		self.assertEqual(relative_direction((0,0), (2,0)),'down')
		self.assertEqual(relative_direction((0,2), (0,0)),'left')
		self.assertEqual(relative_direction((2,0), (0,0)),'up')

		with self.assertRaises(ValueError):
			relative_direction((0,0),(0,0))
			relative_direction((0,0),(1,1))

	def test_when_returns_new_position_of_a_position_and_given_direction(self):
		self.assertEqual(move_pos((0,0),'right'),(0,1))
		self.assertEqual(move_pos((0,0),'down'),(1,0))
		self.assertEqual(move_pos((1,1),'up'),(0,1))
		self.assertEqual(move_pos((1,1),'left'),(1,0))


if __name__ == '__main__':
	unittest.main()
