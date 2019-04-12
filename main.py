import sys
import dungeon

def parse_dungeons():
    # returns a list of Dungeon instances, which are parsed from the
    # files entered on the command line.
    return [dungeon.Dungeon.from_file(path) for path in sys.argv[1:]]


for current_dungeon in parse_dungeons():
    games = list(current_dungeon.games())
    for i, game in enumerate(games):
        # if the player wins a game from games, the loop will terminate.
        # if he loses all games, the program will terminate and no code
        # after the loop will be executed.

        status = game.play()
        if status is game.KILLED:
            if i == len(games) - 1: # if game is the last one
                print('you lose')
                exit()
            else:
                # start the next game
                continue
        elif status is game.WON:
            # start the next dungeon
            print('you win')
            break
        elif status is game.QUIT:
            exit()
        else:
            raise ValueError('invalid game status')
