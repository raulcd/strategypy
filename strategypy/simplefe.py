import json
import sys

if __name__ == "__main__":
    output = sys.stdin.read()
    output_dict = json.loads(output)
    winner = output_dict['winner']
    players = output_dict['players']
    turns = output_dict['turns']

    winner = None if winner is None else players[str(winner)]
    if winner is None:
        print 'No player won and the game ended in {} turns'.format(turns)
    else:
        print 'Player {} won in {} turns'.format(winner, turns)
