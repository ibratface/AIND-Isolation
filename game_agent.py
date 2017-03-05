"""This file contains all the classes you must complete for this project.

You can use the test cases in agent_test.py to help during development, and
augment the test suite with your own test cases to further test your code.

You must test your agent's strength against a set of agents with known
relative strength using tournament.py and include the results in your report.
"""
import random
import sample_players
from random import randint

class Timeout(Exception):
    """Subclass base exception for code clarity."""
    pass

class CustomPlayer:
    def __init__(self, data=None, timeout=1.):
        self.time_left = None
        self.TIMER_THRESHOLD = timeout

    def get_move(self, game, time_left):
        self.time_left = time_left
        legal_moves = game.get_legal_moves(self)

        if len(legal_moves) < 1:
            return (-1, -1)
        else:
            best_move = legal_moves[randint(0, len(legal_moves) - 1)] # use a random move as a default

        try:
            # The search method call (alpha beta or minimax) should happen in
            # here in order to avoid timeout. The try/except block will
            # automatically catch the exception raised by the search method
            # when the timer gets close to expiring
            if self.iterative:
                depth = 1
            else:
                depth = self.search_depth
            while self.iterative or depth <= self.search_depth:
                # print('depth: ', depth)
                # print('search_depth: ', self.search_depth)
                if self.method == 'alphabeta':
                    score, best_move = self.alphabeta(game, depth)
                else: # use minimax by default
                    score, best_move = self.minimax(game, depth)
                depth += 1
        except Timeout:
            # Handle any actions required at timeout, if necessary
            pass

        # Return the best move from the last completed search iteration
        return best_move
