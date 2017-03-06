"""This file contains all the classes you must complete for this project.

You can use the test cases in agent_test.py to help during development, and
augment the test suite with your own test cases to further test your code.

You must test your agent's strength against a set of agents with known
relative strength using tournament.py and include the results in your report.
"""
import random
import math
import operator

class Timeout(Exception):
    """Subclass base exception for code clarity."""
    pass


class Node:

    def __init__(self, game, move=None, parent = None):
        self.utility = 0.
        self.visits = 0.
        self.move = move
        self.game = game
        self.parent = parent
        self.children = None

    def uct(self):
        return self.utility + math.sqrt(math.log(self.parent.visits)/self.visits)

    def __select__(self, node):
        if node.visits == 0 or not node.children:
            return node
        for c in node.children:
            if c.visits == 0:
                return c
        maxnode = node
        maxuct = 0
        for c in node.children:
            uct = c.uct()
            if uct > maxuct:
                maxuct = uct
                maxnode = c
        return self.__select__(maxnode)

    def select(self):
        return self.__select__(self)

    def expand(self):
        if not self.children:
            moves = self.game.get_legal_moves(self.game.active_player)
            if moves: self.children = [ Node(self.game.forecast_move(m), m, self) for m in moves ]

    def simulate(self, player, max_sims=10):
        sims = 1
        wins = 0
        while sims < max_sims:
            sim = self.game.copy()
            moves = sim.get_legal_moves(sim.active_player)
            while moves:
                if player.time_left() < player.TIMER_THRESHOLD:
                    raise Timeout()
                sim.apply_move(moves[random.randint(0, len(moves) - 1)])
                moves = sim.get_legal_moves(sim.active_player)
            sims += 1
            if self.game.active_player == sim.inactive_player:
                wins += 1
        return 1. * wins / sims

    def backpropagate(self, score):
        self.visits += 1
        self.utility += score
        if self.parent:
            self.parent.backpropagate(score)

    def advance(self, move):
        # print (self.game.active_player)
        # print (self.game.get_legal_moves())
        # print (move)
        # print (self.game.to_string())
        if self.children:
            for c in self.children:
                if c.move == move:
                    c.parent = None
                    return c
        assert False


class CustomPlayer:

    def __init__(self, data=None, timeout=1.):
        self.time_left = None
        self.TIMER_THRESHOLD = timeout
        self.root = None

    def get_move(self, game, time_left):
        self.time_left = time_left

        # opponent = game.get_opponent(self)
        # own_moves = game.get_legal_moves(self)
        # opp_moves = game.get_legal_moves(opponent)
        # if len(own_moves) < 1:
        #     return (-1, -1)
        # print ('LEGAL MOVES:', own_moves)
        # print ('move_count: ', game.move_count)
        # print (game.to_string())

        if game.move_count < 4:
            self.root = Node(game)
        else:
            # maintain consistency with game state
            # advance to the node that reflects game state
            opponent = game.get_opponent(self)
            opp_move = game.get_player_location(opponent)
            self.root = self.root.advance(opp_move)
            # if not self.root:
            #     assert game.utility(self) != 0

        try:
            while time_left() > self.TIMER_THRESHOLD:
                node = self.root.select()
                node.expand()
                score = node.simulate(self)
                node.backpropagate(score)
        except Timeout:
            print ('TIIMEOUT!!!')
            pass

        if self.root.children:
            scores = [ (1.*c.visits, c.move) for c in self.root.children ]
            # print ('scores: ', scores)
            _, best_move = max(scores)
            self.root = self.root.advance(best_move)
        else:
            best_move = (-1, -1)

        return best_move
