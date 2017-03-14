import random
import math
import itertools


class Timeout(Exception):
    """Subclass base exception for code clarity."""
    pass


class Node:

    def __init__(self, move=None, parent = None):
        self.utility = 0
        self.visits = 0
        self.move = move
        self.parent = parent
        self.children = None

    def to_dict(self, depth=11):
        dic = {}
        dic['v'] = (self.utility, self.visits)
        dic['m'] = self.move
        if depth > 0 and self.children:
            dic['c'] = tuple( c.to_dict(depth-1) for c in self.children )
        return dic

    def from_dict(self, dic):
        self.utility, self.visits = dic['v']
        # print ('from_dict', self.utility, self.visits, dic['m'])
        if 'c' in dic:
            self.children = tuple( Node(tuple(c['m']), self).from_dict(c) for c in dic['c'] )
        return self

    def default(self):
        moves = itertools.product(range(7), range(7))
        self.children = tuple( Node(m, self) for m in moves )
        for c in self.children:
            moves = itertools.product(range(7), range(7))
            c.children = tuple( Node(m, c) for m in moves if m != c.move )
        return self


class CustomPlayer:

    def __init__(self, data=None, timeout=1.):
        self.time_left = None
        self.TIMER_THRESHOLD = timeout
        self.root = None
        self.tree = Node().from_dict(data) if data else Node().default()
        self.C = 0.35
        self.rollout = self.rollout_random

    def uct(self, node):
        return (1. * node.utility / node.visits) + (math.sqrt(math.log(node.parent.visits) / node.visits) * self.C)

    def score(self, node):
        return 1. * node.utility / node.visits

    def select(self, node, state):
        if not node.children:
            return node

        choice = next((c for c in node.children if c.visits == 0), None)
        if not choice:
            _, choice = max(((self.uct(c), c) for c in node.children), key=lambda x: x[0])
        state.apply_move(choice.move)
        return self.select(choice, state)

    def expand(self, node, state):
        if not node.children:
            node.children = tuple( Node(m, node) for m in state.get_legal_moves(state.active_player) )

    def rollout_random(self, node, state):
        sim = state
        moves = sim.get_legal_moves(sim.active_player)
        while moves:
            sim.apply_move(moves[random.randint(0, len(moves) - 1)])
            moves = sim.get_legal_moves(sim.active_player)
        return 1 if sim.inactive_player == state.active_player else 0

    def simulate(self, node, state):
        if node.children:
            c = node.children[random.randint(0, len(node.children) - 1)]
            self.backpropagate(c, self.rollout(c, state))
        else:
            self.backpropagate(node, 1)

    def backpropagate(self, node, score):
        node.visits += 1
        node.utility += score
        if node.parent:
            self.backpropagate(node.parent, 1 - score)

    def advance(self, node, move):
        for c in node.children:
            if c.move == move:
                # c.parent = None
                return c

    def get_move(self, game, time_left):
        if game.move_count < 2:
            self.root = self.tree

        if self.root:
            # attempt to maintain consistency with game
            # advance to the node that reflects current game state
            opponent = game.get_opponent(self)
            opp_move = game.get_player_location(opponent)
            if opp_move:
                self.root = self.advance(self.root, opp_move)

        if not self.root:
            # new game state, new node
            self.root = Node()
            self.expand(self.root, game)

        self.time_left = time_left
        while self.time_left() > self.TIMER_THRESHOLD:
            state = game.copy()
            node = self.select(self.root, state)
            self.expand(node, state)
            self.simulate(node, state)

        best_move = (-1, -1)
        if self.root.children:
            # If we haven't lost, make the best move
            _, best_move = max([ (self.score(c), c.move) for c in self.root.children ])
            self.root = self.advance(self.root, best_move)

        # print ('BEST_MOVE:', best_move)
        # print (game.to_string())

        return best_move
