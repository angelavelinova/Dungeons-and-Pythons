import sys
import dungeon
import utils

def parse_dungeons():
    # returns a list of Dungeon instances, which are parsed from the
    # files entered on the command line.
    return [dungeon.Dungeon.from_file(path) for path in sys.argv[1:]]

dungeons = parse_dungeons()

def start():
    for current_dungeon in dungeons:
        games = list(current_dungeon.games())
        for i, game in enumerate(games):
            status = game.play()
            if status is game.KILLED:
                if i == len(games) - 1: # if game is the last one
                    return 'lost'
                else:
                    # start the next game
                    continue
            elif status is game.WON:
                # start the next dungeon
                break
            elif status is game.QUIT:
                return 'quit'
            else:
                raise ValueError('invalid game status')
    return 'won'

while True:
    status = start()
    if status == 'quit':
        break
    else:
        if status == 'won':
            print('you win')
        else:
            print('you lose')
            
        print('press space to play again')
        char = utils.get_char()
        if char != " ":
            break
