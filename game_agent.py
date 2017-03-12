import random
import math


class Timeout(Exception):
    """Subclass base exception for code clarity."""
    pass


class Node:

    def __init__(self, move=None, parent = None):
        self.utility = 0.
        self.visits = 0.
        self.move = move
        self.parent = parent
        self.children = None


class CustomPlayer:

    DEFAULTS = {
        'C': 0.3,
        'rollout': 'random',
    }

    def __init__(self, data=None, timeout=1.):
        self.time_left = None
        self.TIMER_THRESHOLD = timeout
        self.root = None
        data = data if data else self.DEFAULTS
        self.C = data.get('C', self.DEFAULTS['C'])
        self.rollout = self.rollout_random

    def uct(self, node):
        return (node.utility / node.visits) + (math.sqrt(math.log(node.parent.visits) / node.visits) * self.C)

    def score(self, node):
        return node.utility / node.visits

    def select(self, node):
        if not node.children:
            return node

        choice = next((c for c in node.children if c.visits == 0), None)
        if choice: return choice

        _, choice = max(((self.uct(c), c) for c in node.children), key=lambda x: x[0])
        return self.select(choice)

    def forward(self, state, node):
        moves = []
        while node.parent:
            moves.append(node.move)
            node = node.parent
        forecast = state.copy()
        for m in reversed(moves):
            forecast.apply_move(m)
        return forecast

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
                c.parent = None
                return c

    def get_move(self, game, time_left):
        self.time_left = time_left
        best_move = (-1, -1)

        if game.move_count < 4:
            self.root = Node()
            self.expand(self.root, game)
        elif self.root:
            # maintain consistency with game state
            # advance to the node that reflects game state
            opponent = game.get_opponent(self)
            opp_move = game.get_player_location(opponent)
            self.root = self.advance(self.root, opp_move)

        if self.root:
            # Do mcts while we have time
            while self.time_left() > self.TIMER_THRESHOLD:
                node = self.select(self.root)
                state = self.forward(game, node)
                self.expand(node, state)
                self.simulate(node, state)

            # Pick the best move if any
            if self.root.children:
                _, best_move = max([ (self.score(c), c.move) for c in self.root.children ])
                # print ('SCORES: ', scores)
                # print ('BEST_MOVE:', best_move)
                self.root = self.advance(self.root, best_move)
        else:
            own_moves = game.get_legal_moves(self)
            if own_moves: best_move = own_moves[0]

        # print ('BEST_MOVE:', best_move)
        # print (game.to_string())

        return best_move
