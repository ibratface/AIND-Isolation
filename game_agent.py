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
        self.children = []

    def uct(self):
        val = self.utility/self.visits + math.sqrt(2. * math.log(self.parent.visits) / self.visits)
        # print ('UCT: ', self.visits, self.parent.visits, self.utility, val)
        # print (self.game.to_string())
        return val

    def score(self):
        return 0 if self.visits == 0 else self.utility / self.visits

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
            if uct >= maxuct:
                maxuct = uct
                maxnode = c
        # print ('SELECT Node: ')
        # print (node.game.to_string())
        return self.__select__(maxnode)

    def select(self):
        return self.__select__(self)

    def expand(self):
        if len(self.children) == 0:
            moves = self.game.get_legal_moves(self.game.active_player)
            if moves: self.children = [ Node(self.game.forecast_move(m), m, self) for m in moves ]

    def rollout(self):
        sim = self.game.copy()
        moves = sim.get_legal_moves(sim.active_player)
        while moves:
            sim.apply_move(moves[random.randint(0, len(moves) - 1)])
            moves = sim.get_legal_moves(sim.active_player)
        return 1 if sim.inactive_player == self.parent.game.active_player else 0

    def simulate(self, player):
        if self.children:
            c = self.children[random.randint(0, len(self.children) - 1)]
            c.backpropagate(c.rollout())
        # for c in self.children:
        #     sim = c.rollout()
        #     c.backpropagate(1 if sim.inactive_player == c.game.active_player else 0)

    def backpropagate(self, score):
        self.visits += 1
        self.utility += score
        if self.parent:
            self.parent.backpropagate(1 - score)

    def advance(self, move):
        # print (self.game.active_player)
        # print (self.game.get_legal_moves())
        # print (move)
        # print (self.game.to_string())
        for c in self.children:
            if c.move == move:
                c.parent = None
                return c
        # assert False


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
        elif self.root:
            # maintain consistency with game state
            # advance to the node that reflects game state
            opponent = game.get_opponent(self)
            opp_move = game.get_player_location(opponent)
            self.root = self.root.advance(opp_move)

        best_move = (-1, -1)

        if self.root:
            # Do mcts while we have time
            try:
                while time_left() > self.TIMER_THRESHOLD:
                    node = self.root.select()
                    node.expand()
                    node.simulate(self)
            except Timeout:
                print ('TIIMEOUT!!!')
                pass

            # Pick the best move
            if self.root.children:
                scores = [ (c.score(), c.move) for c in self.root.children ]
                _, best_move = max(scores)
                print ('SCORES: ', scores)
                # print ('BEST_MOVE:', best_move)
                self.root = self.root.advance(best_move)
        else:
            own_moves = game.get_legal_moves(self)
            if own_moves: best_move = own_moves[0]

        print ('BEST_MOVE:', best_move)
        print (game.to_string())

        return best_move
