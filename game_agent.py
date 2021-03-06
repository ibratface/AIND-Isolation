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

def mcs(game, player, max_sims, max_time, stage=0):
    wins = 0
    sims = 0
    time_start = player.time_left()

    while sims < max_sims and time_start - player.time_left() < max_time:
        if player.time_left() < 1:
            # print('Monte Carlo ran out of time at stage: {} simulation number: {}'.format(stage, sims))
            raise Timeout()
        sim = game.copy()
        while True:
            moves = sim.get_legal_moves(sim.active_player)
            if moves:
                sim.apply_move(moves[randint(0, len(moves) - 1)])
            else:
                if player == sim.inactive_player:
                    wins += 1
                break
        sims += 1

    return wins, sims + 1

def mcs_score(game, player):
    opponent = game.get_opponent(player)
    own_moves = len(game.get_legal_moves(player))
    opp_moves = len(game.get_legal_moves(opponent))

    if own_moves == 0 and game.active_player == player:
        return float("-inf")

    if opp_moves == 0 and game.active_player == opponent:
        return float("inf")

    wins, sims = mcs(game, player, 50, 2)
    return wins / sims

def aggressive_score(game, player):
    opponent = game.get_opponent(player)
    own_moves = len(game.get_legal_moves(player))
    opp_moves = len(game.get_legal_moves(opponent))

    if own_moves == 0 and game.active_player == player:
        return float("-inf")

    if opp_moves == 0 and game.active_player == opponent:
        return float("inf")

    blank_spaces = game.height * game.width - game.move_count - 2

    return float(blank_spaces - opp_moves)

def balanced_score(game, player):
    opponent = game.get_opponent(player)
    own_moves = len(game.get_legal_moves(player))
    opp_moves = len(game.get_legal_moves(opponent))

    if own_moves == 0 and game.active_player == player:
        return float("-inf")

    if opp_moves == 0 and game.active_player == opponent:
        return float("inf")

    blank_spaces = game.height * game.width - game.move_count - 2

    return float(own_moves) * (blank_spaces - opp_moves)

def custom_score(game, player):
    """Calculate the heuristic value of a game state from the point of view
    of the given player.

    Note: this function should be called from within a Player instance as
    `self.score()` -- you should not need to call this function directly.

    Parameters
    ----------
    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of the
        game (e.g., player locations and blocked cells).

    player : object
        A player instance in the current game (i.e., an object corresponding to
        one of the player objects `game.__player_1__` or `game.__player_2__`.)

    Returns
    -------
    float
        The heuristic value of the current game state to the specified player.
    """
    return mcs_score(game, player)

class CustomPlayer:
    """Game-playing agent that chooses a move using your evaluation function
    and a depth-limited minimax algorithm with alpha-beta pruning. You must
    finish and test this player to make sure it properly uses minimax and
    alpha-beta to return a good move before the search time limit expires.

    Parameters
    ----------
    search_depth : int (optional)
        A strictly positive integer (i.e., 1, 2, 3,...) for the number of
        layers in the game tree to explore for fixed-depth search. (i.e., a
        depth of one (1) would only explore the immediate sucessors of the
        current state.)

    score_fn : callable (optional)
        A function to use for heuristic evaluation of game states.

    iterative : boolean (optional)
        Flag indicating whether to perform fixed-depth search (False) or
        iterative deepening search (True).

    method : {'minimax', 'alphabeta'} (optional)
        The name of the search method to use in get_move().

    timeout : float (optional)
        Time remaining (in milliseconds) when search is aborted. Should be a
        positive value large enough to allow the function to return before the
        timer expires.
    """

    def __init__(self, search_depth=3, score_fn=custom_score,
                 iterative=True, method='minimax', timeout=10.):
        self.search_depth = search_depth
        self.iterative = iterative
        self.score = score_fn
        self.method = method
        self.time_left = None
        self.TIMER_THRESHOLD = timeout

    def get_move(self, game, legal_moves, time_left):
        """Search for the best move from the available legal moves and return a
        result before the time limit expires.

        This function must perform iterative deepening if self.iterative=True,
        and it must use the search method (minimax or alphabeta) corresponding
        to the self.method value.

        **********************************************************************
        NOTE: If time_left < 0 when this function returns, the agent will
              forfeit the game due to timeout. You must return _before_ the
              timer reaches 0.
        **********************************************************************

        Parameters
        ----------
        game : `isolation.Board`
            An instance of `isolation.Board` encoding the current state of the
            game (e.g., player locations and blocked cells).

        legal_moves : list<(int, int)>
            A list containing legal moves. Moves are encoded as tuples of pairs
            of ints defining the next (row, col) for the agent to occupy.

        time_left : callable
            A function that returns the number of milliseconds left in the
            current turn. Returning with any less than 0 ms remaining forfeits
            the game.

        Returns
        -------
        (int, int)
            Board coordinates corresponding to a legal move; may return
            (-1, -1) if there are no available legal moves.
        """

        self.time_left = time_left

        # Perform any required initializations, including selecting an initial
        # move from the game board (i.e., an opening book), or returning
        # immediately if there are no legal moves
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

    def minimax(self, game, depth, maximizing_player=True):
        """Implement the minimax search algorithm as described in the lectures.

        Parameters
        ----------
        game : isolation.Board
            An instance of the Isolation game `Board` class representing the
            current game state

        depth : int
            Depth is an integer representing the maximum number of plies to
            search in the game tree before aborting

        maximizing_player : bool
            Flag indicating whether the current search depth corresponds to a
            maximizing layer (True) or a minimizing layer (False)

        Returns
        -------
        float
            The score for the current search branch

        tuple(int, int)
            The best move for the current branch; (-1, -1) for no legal moves

        Notes
        -----
            (1) You MUST use the `self.score()` method for board evaluation
                to pass the project unit tests; you cannot call any other
                evaluation function directly.
        """
        if self.time_left() < self.TIMER_THRESHOLD:
            raise Timeout()

        moves = game.get_legal_moves(game.active_player)
        if not moves:
            return (game.utility(self), (-1, -1))

        if depth < 2:
            scores = [ (self.score(game.forecast_move(m), self), m) for m in moves ]
        else:
            # recurse
            scores = [ (self.minimax(game.forecast_move(m), depth-1, not maximizing_player)[0], m) for m in moves ]
        best_score = max(scores) if maximizing_player else min(scores)
        # print ('depth: ', depth)
        # print('len(scores): ', len(scores))
        # print('scores: ', scores)
        # print('best_score: ', best_score)
        return best_score


    def alphabeta(self, game, depth, alpha=float("-inf"), beta=float("inf"), maximizing_player=True):
        """Implement minimax search with alpha-beta pruning as described in the
        lectures.

        Parameters
        ----------
        game : isolation.Board
            An instance of the Isolation game `Board` class representing the
            current game state

        depth : int
            Depth is an integer representing the maximum number of plies to
            search in the game tree before aborting

        alpha : float
            Alpha limits the lower bound of search on minimizing layers

        beta : float
            Beta limits the upper bound of search on maximizing layers

        maximizing_player : bool
            Flag indicating whether the current search depth corresponds to a
            maximizing layer (True) or a minimizing layer (False)

        Returns
        -------
        float
            The score for the current search branch

        tuple(int, int)
            The best move for the current branch; (-1, -1) for no legal moves

        Notes
        -----
            (1) You MUST use the `self.score()` method for board evaluation
                to pass the project unit tests; you cannot call any other
                evaluation function directly.
        """
        if self.time_left() < self.TIMER_THRESHOLD:
            raise Timeout()

        moves = game.get_legal_moves(game.active_player)
        if not moves:
            return (game.utility(self), (-1, -1))

        scores = []
        if depth < 2:
            if maximizing_player:
                for m in moves:
                    score = self.score(game.forecast_move(m), self)
                    scores.append((score, m))
                    if score >= beta:
                        break;
                    if score > alpha:
                        alpha = score
                best_score = max(scores)
            else:
                for m in moves:
                    score = self.score(game.forecast_move(m), self)
                    scores.append((score, m))
                    if score <= alpha:
                        break
                    if score < beta:
                        beta = score
                best_score = min(scores)
        else:
            if maximizing_player:
                for m in moves:
                    score = self.alphabeta(game.forecast_move(m), depth-1, alpha, beta, not maximizing_player)[0]
                    scores.append((score, m))
                    if score >= beta:
                        break;
                    if score > alpha:
                        alpha = score
                best_score = max(scores)
            else:
                for m in moves:
                    score = self.alphabeta(game.forecast_move(m), depth-1, alpha, beta, not maximizing_player)[0]
                    scores.append((score, m))
                    if score <= alpha:
                        break
                    if score < beta:
                        beta = score
                best_score = min(scores)
        # print ('depth: ', depth)
        # print('len(scores): ', len(scores))
        # print('scores: ', scores)
        # print('best_score: ', best_score)
        return best_score
