import sys
import dungeon
import utils

class GameOver(Exception):
    pass

def parse_dungeons():
    # returns a list of Dungeon instances, which are parsed from the
    # files entered on the command line.
    return [dungeon.Dungeon.from_file(path) for path in sys.argv[1:]]


dungeons = parse_dungeons()

def start_game():
    for current_dungeon in dungeons:
        games = list(current_dungeon.games())
        for i, game in enumerate(games):
            # if the player wins a game from games, the loop will terminate.
            # if he loses all games, the program will terminate and no code
            # after the loop will be executed.

            status = game.play()
            if status is game.KILLED:
                if i == len(games) - 1: # if game is the last one
                    raise GameOver('you lose')
                else:
                    # start the next game
                    continue
            elif status is game.WON:
                # start the next dungeon
                break
            elif status is game.QUIT:
                raise GameOver('quit')
            else:
                raise ValueError('invalid game status')
    raise GameOver('you won')

while True:
    try:
        start_game()
    except GameOver as go:
        if str(go) == 'quit':
            break

        print(go)
        print('press space to play again')
        char = utils.get_char()
        if char != " ":
            break
