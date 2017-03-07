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

    def __init__(self, move=None, parent = None):
        self.utility = 0.
        self.visits = 0.
        self.move = move
        self.parent = parent
        self.children = []

class CustomPlayer:

    DEFAULTS = {
        'C': 0.35,
        'rollout': 'random',
    }

    def __init__(self, data=DEFAULTS, timeout=1.):
        self.time_left = None
        self.TIMER_THRESHOLD = timeout
        self.root = None
        self.C = data.get('C', self.DEFAULTS['C'])
        self.rollout = self.rollout_random

    def uct(self, node):
        val = (node.utility / node.visits) + (math.sqrt(math.log(node.parent.visits) / node.visits) * self.C)
        # print ('UCT: ', self.visits, self.parent.visits, self.utility, val)
        # print (self.game.to_string())
        return val

    def score(self, node):
        return 0 if node.visits == 0 else node.utility / node.visits

    def select(self, node):
        # if self.time_left() < self.TIMER_THRESHOLD:
        #     raise Timeout("Select() {}".format(self.time_left()))
        if node.visits == 0 or not node.children:
            return node
        for c in node.children:
            if c.visits == 0:
                return c
        maxnode = node
        maxuct = 0
        for c in node.children:
            uct = self.uct(c)
            if uct >= maxuct:
                maxuct = uct
                maxnode = c
        # print ('SELECT Node: ')
        # print (node.game.to_string())
        return self.select(maxnode)

    def forward(self, state, node):
        moves = []
        while node.parent:
            moves.append(node.move)
            node = node.parent
        # print (moves)
        moves.reverse()
        forecast = state.copy()
        for m in moves:
            forecast.apply_move(m)
        return forecast

    def expand(self, node, state):
        # print ("Expand() Start: {}".format(self.time_left()))
        #
        # if self.time_left() < self.TIMER_THRESHOLD:
        #     raise Timeout("Expand() {}".format(self.time_left()))

        if len(node.children) == 0:
            moves = state.get_legal_moves(state.active_player)
            for m in moves:
                node.children.append(Node(m, node))

        # print ("Expand() End: {}".format(self.time_left()))

    def improved_score(self, game):
        own_moves = len(game.get_legal_moves(game.active_player))
        opp_moves = len(game.get_legal_moves(game.inactive_player))

        if opp_moves == 0 and own_moves > 0:
            return float("inf")
        elif own_moves == 0:
            return float("-inf")

        return own_moves - opp_moves

    def rollout_improved(self, node, state):
        sim = state.forecast_move(node.move)
        moves = sim.get_legal_moves(sim.active_player)
        while moves:
            _, move = max([ (self.improved_score(sim.forecast_move(m)), m) for m in moves ])
            sim.apply_move(move)
            moves = sim.get_legal_moves(sim.active_player)
        return 1 if sim.inactive_player == state.active_player else 0

    def rollout_random(self, node, state):
        # print ("Rollout() Start: {}".format(self.time_left()))
        #
        # if self.time_left() < self.TIMER_THRESHOLD:
        #     raise Timeout("Rollout() {}".format(self.time_left()))

        sim = state.forecast_move(node.move)
        moves = sim.get_legal_moves(sim.active_player)
        while moves:
            # if self.time_left() < self.TIMER_THRESHOLD:
            #     raise Timeout("Rollout() {}".format(self.time_left()))
            sim.apply_move(moves[random.randint(0, len(moves) - 1)])
            moves = sim.get_legal_moves(sim.active_player)

        # print ("Rollout() End: {}".format(self.time_left()))
        return 1 if sim.inactive_player == state.active_player else 0

    def simulate(self, node, state):
        # print ("Simulate() Start: {}".format(self.time_left()))

        # if self.time_left() < self.TIMER_THRESHOLD:
        #     raise Timeout("Simulate() {}".format(self.time_left()))

        if node.children:
            c = node.children[random.randint(0, len(node.children) - 1)]
            self.backpropagate(c, self.rollout(c, state))
            # for c in node.children:
            #     self.backpropagate(c, self.rollout(c, state))
        else:
            # terminal node, backprop a win
            self.backpropagate(node, 1)

        # print ("Simulate() End: {}".format(self.time_left()))

    def backpropagate(self, node, score):
        node.visits += 1
        node.utility += score
        if node.parent:
            self.backpropagate(node.parent, 1 - score)

    def advance(self, node, move):
        # print (self.game.active_player)
        # print (self.game.get_legal_moves())
        # print (move)
        # print (self.game.to_string())
        for c in node.children:
            if c.move == move:
                c.parent = None
                return c
        # assert False

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
            self.root = Node()
            self.expand(self.root, game)
        elif self.root:
            # maintain consistency with game state
            # advance to the node that reflects game state
            opponent = game.get_opponent(self)
            opp_move = game.get_player_location(opponent)
            self.root = self.advance(self.root, opp_move)

        best_move = (-1, -1)

        if self.root:
            # Do mcts while we have time
            try:
                while self.time_left() > self.TIMER_THRESHOLD:
                    # print ("Before Select(): {}".format(self.time_left()))
                    node = self.select(self.root)
                    # if self.time_left() < self.TIMER_THRESHOLD: break
                    # print ("Before Forward(): {}".format(self.time_left()))
                    state = self.forward(game, node)
                    # if self.time_left() < self.TIMER_THRESHOLD: break
                    # print ("Before Expand(): {}".format(self.time_left()))
                    self.expand(node, state)
                    # if self.time_left() < self.TIMER_THRESHOLD: break
                    # print ("Before Simulate: {}".format(self.time_left()))
                    self.simulate(node, state)
            except Timeout as e:
                print (e)
                pass

            # if self.time_left() < 0:
            #     print ('TIME EXCEEDED! {}'.format(self.time_left()))
            #     assert False

            # Pick the best move if any
            if self.root.children:
                scores = [ (self.score(c), c.move, c.visits) for c in self.root.children ]
                _, best_move, _ = max(scores)
                # print ('SCORES: ', scores)
                # print ('BEST_MOVE:', best_move)
                self.root = self.advance(self.root, best_move)
        else:
            own_moves = game.get_legal_moves(self)
            if own_moves: best_move = own_moves[0]

        # print ('BEST_MOVE:', best_move)
        # print (game.to_string())

        return best_move
