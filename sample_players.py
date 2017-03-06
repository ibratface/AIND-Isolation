"""This file contains a collection of player classes for comparison with your
own agent and example heuristic functions.
"""

from random import randint


class Timeout(Exception):
    """Subclass base exception for code clarity."""
    pass


def null_score(game, player):
    """This heuristic presumes no knowledge for non-terminal states, and
    returns the same uninformative value for all other states.

    Parameters
    ----------
    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of the
        game (e.g., player locations and blocked cells).

    player : hashable
        One of the objects registered by the game object as a valid player.
        (i.e., `player` should be either game.__player_1__ or
        game.__player_2__).

    Returns
    ----------
    float
        The heuristic value of the current game state.
    """

    if game.is_loser(player):
        return float("-inf")

    if game.is_winner(player):
        return float("inf")

    return 0.


def open_move_score(game, player):
    """The basic evaluation function described in lecture that outputs a score
    equal to the number of moves open for your computer player on the board.

    Parameters
    ----------
    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of the
        game (e.g., player locations and blocked cells).

    player : hashable
        One of the objects registered by the game object as a valid player.
        (i.e., `player` should be either game.__player_1__ or
        game.__player_2__).

    Returns
    ----------
    float
        The heuristic value of the current game state
    """
    if game.is_loser(player):
        return float("-inf")

    if game.is_winner(player):
        return float("inf")

    return float(len(game.get_legal_moves(player)))


def improved_score(game, player):
    """The "Improved" evaluation function discussed in lecture that outputs a
    score equal to the difference in the number of moves available to the
    two players.

    Parameters
    ----------
    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of the
        game (e.g., player locations and blocked cells).

    player : hashable
        One of the objects registered by the game object as a valid player.
        (i.e., `player` should be either game.__player_1__ or
        game.__player_2__).

    Returns
    ----------
    float
        The heuristic value of the current game state
    """
    if game.is_loser(player):
        return float("-inf")

    if game.is_winner(player):
        return float("inf")

    own_moves = len(game.get_legal_moves(player))
    opp_moves = len(game.get_legal_moves(game.get_opponent(player)))
    return float(own_moves - opp_moves)


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
    return mcs_score(game, player)


directions = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
              (1, -2),  (1, 2), (2, -1),  (2, 1)]


def get_max_depth(pos, blanks, depth=0, max_depth=0):
    if max_depth < depth:
        max_depth = depth

    valid_moves = [ pos + d for d in directions if pos + d in blanks ]
    for m in valid_moves:
        blanks.remove(m)
        max_depth = get_max_depth(m, blanks, depth+1, max_depth)
        blanks.append(m)

    return max_depth


def depth_score(game, player):
    opponent = game.get_opponent(player)
    own_moves = len(game.get_legal_moves(player))
    opp_moves = len(game.get_legal_moves(opponent))

    if opp_moves == 0 and own_moves > 0:
        return float("inf")
    elif own_moves == 0:
        return float("-inf")

    total_spaces = game.height * game.width
    blank_spaces = total_spaces - game.move_count
    # stage = 1. * game.move_count / total_spaces * 100
    #
    # if stage < 65:
    #     wins, sims = mcs(game, player, 50, 2)
    #     score = wins / sims
    #     # score = (1. - opp_moves / blank_spaces)
    # else:
    own_pos = game.get_player_location(player)
    #opp_pos = game.get_player_location(opponent)
    blanks = game.get_blank_spaces()
    score = get_max_depth(own_pos, blanks) #- get_max_depth(opp_pos, blanks)
    return score

class SamplePlayer:
    def __init__(self, data=None, timeout=10., search_depth=3, score_fn=custom_score,
                 iterative=True, method='minimax'):
        self.search_depth = search_depth
        self.iterative = iterative
        self.score = score_fn
        self.method = method
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

    def minimax(self, game, depth, maximizing_player=True):
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


class RandomPlayer():
    """Player that chooses a move randomly."""

    def get_move(self, game, time_left):
        """Randomly select a move from the available legal moves.

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
        ----------
        (int, int)
            A randomly selected legal move; may return (-1, -1) if there are
            no available legal moves.
        """

        legal_moves = game.get_legal_moves(self)
        if not legal_moves:
            return (-1, -1)
        return legal_moves[randint(0, len(legal_moves) - 1)]


class GreedyPlayer():
    """Player that chooses next move to maximize heuristic score. This is
    equivalent to a minimax search agent with a search depth of one.
    """

    def __init__(self, score_fn=open_move_score):
        self.score = score_fn

    def get_move(self, game, time_left):
        """Select the move from the available legal moves with the highest
        heuristic score.

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
        ----------
        (int, int)
            The move in the legal moves list with the highest heuristic score
            for the current game state; may return (-1, -1) if there are no
            legal moves.
        """

        legal_moves = game.get_legal_moves(self)
        if not legal_moves:
            return (-1, -1)
        _, move = max([(self.score(game.forecast_move(m), self), m) for m in legal_moves])
        return move


class HumanPlayer():
    """Player that chooses a move according to user's input."""

    def get_move(self, game, time_left):
        """
        Select a move from the available legal moves based on user input at the
        terminal.

        **********************************************************************
        NOTE: If testing with this player, remember to disable move timeout in
              the call to `Board.play()`.
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
        ----------
        (int, int)
            The move in the legal moves list selected by the user through the
            terminal prompt; automatically return (-1, -1) if there are no
            legal moves
        """
        legal_moves = game.get_legal_moves(self)
        if not legal_moves:
            return (-1, -1)

        print(('\t'.join(['[%d] %s' % (i, str(move)) for i, move in enumerate(legal_moves)])))

        valid_choice = False
        while not valid_choice:
            try:
                index = int(input('Select move index:'))
                valid_choice = 0 <= index < len(legal_moves)

                if not valid_choice:
                    print('Illegal move! Try again.')

            except ValueError:
                print('Invalid index! Try again.')

        return legal_moves[index]


if __name__ == "__main__":
    from isolation import Board

    # create an isolation board (by default 7x7)
    player1 = RandomPlayer()
    player2 = GreedyPlayer()
    game = Board(player1, player2)

    # place player 1 on the board at row 2, column 3, then place player 2 on
    # the board at row 0, column 5; display the resulting board state.  Note
    # that .apply_move() changes the calling object
    game.apply_move((2, 3))
    game.apply_move((0, 5))
    print(game.to_string())

    # players take turns moving on the board, so player1 should be next to move
    assert(player1 == game.active_player)

    # get a list of the legal moves available to the active player
    print(game.get_legal_moves())

    # get a successor of the current state by making a copy of the board and
    # applying a move. Notice that this does NOT change the calling object
    # (unlike .apply_move()).
    new_game = game.forecast_move((1, 1))
    assert(new_game.to_string() != game.to_string())
    print("\nOld state:\n{}".format(game.to_string()))
    print("\nNew state:\n{}".format(new_game.to_string()))

    # play the remainder of the game automatically -- outcome can be "illegal
    # move" or "timeout"; it should _always_ be "illegal move" in this example
    winner, history, outcome = game.play()
    print("\nWinner: {}\nOutcome: {}".format(winner, outcome))
    print(game.to_string())
    print("Move history:\n{!s}".format(history))
