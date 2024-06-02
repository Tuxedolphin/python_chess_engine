from chess_logic import *
import random
import copy


def return_move(move: Move, evaluation) -> tuple[Move, str, int]:
    """
    Returns the move with the correct format.

    Assumes to always promote to queen for now
    """

    if move.is_pawn_promotion:
        return move, "Q", evaluation

    return move, "", evaluation


def return_random_move(moves: list[Move]) -> Move:
    """Returns a random move from a list of moves"""

    # Change the seed to make it more random
    random.seed()

    length = len(moves)
    if not length:
        raise ValueError("No item in list of moves")

    if length == 1:
        return moves[0]

    else:
        return moves[random.randint(0, length - 1)]


def random_move_ai(valid_moves: list) -> Move:
    """An AI which randomly makes a move in the list of valid moves"""

    move = valid_moves[random.randint(0, len(valid_moves) - 1)]

    return return_move(move)


def simple_materialistic_ai(valid_moves: list) -> Move:
    """
    An AI which returns the move which captured the most material.
    If multiple moves captures the same amount of material, it will randomly return a move.

    A pawn promotion is counted as 'capturing' 8 points of material.
    """

    # Keep track of values of each move
    values = {
        "Q": 9,
        "R": 5,
        "B": 3,
        "N": 3,
        "p": 1,
        "promotion": 8,
    }

    # Keep track of the move which gains/ captures the most points
    max_points = 0

    # Keeps track of the moves which has the max points
    best_moves = []

    for move in valid_moves:
        if not move.piece_captured:
            value = 0

        elif move.is_pawn_promotion:
            value = values["promotion"]

        else:
            value = values[move.piece_captured[1]]

        if value > max_points:
            max_points = value
            best_moves = [move]

        elif value == max_points:
            best_moves.append(move)

    # Randomly selects a move
    best_move = return_random_move(best_moves)

    return return_move(best_move, max_points)


def materialistic_minimax_ai(
    valid_moves: list[Move],
    game_state: GameState,
    depth: int = 2,
    current_depth: int = 0,
) -> tuple[Move, str, int]:
    """
    An AI which only considers material, except that it will recursively call itself up
    to a maximum depth of "depth" ply using a minimax algorithm.

    No alpha beta pruning used
    """

    # Keeps track of the number of ply
    current_depth += 1
    
    # Keep track of who's turn it is
    white_move = game_state.white_move

    # Keep track of the move which gains/ captures the most points
    best_net_evaluation = -100000 if white_move else 100000

    # Keeps track of the moves which has the max points
    best_net_moves = []

    # Finds the best moves for the current iteration
    for move in valid_moves:

        # Creates a copy of the game state so that it is not altered and gets a new evaluation
        copied_game_state = copy.deepcopy(game_state)
        copied_game_state.make_move(move)

        # If it is the last iteration, we simply get the evaluation so we don't have to generate all valid moves
        if current_depth == depth:
            evaluation = (
                copied_game_state.white_material - copied_game_state.black_material
            )
            best_net_evaluation, best_net_moves = compare_evaluations(
                move,
                evaluation,
                best_net_evaluation,
                best_net_moves,
                white_move,
            )

        else:
            copied_valid_moves = copied_game_state.get_valid_moves()

            # If there are no valid moves, it is either checkmate or stalemate, and update accordingly
            if not copied_valid_moves:
                if game_state.in_check:
                    evaluation = -10000 if white_move else 10000

                else:
                    evaluation = 0

            else:
                # Call recursion to get the evaluation for every move
                _, _, evaluation = materialistic_minimax_ai(
                    copied_valid_moves,
                    copied_game_state,
                    depth,
                    current_depth=current_depth,
                )

            best_net_evaluation, best_net_moves = compare_evaluations(
                move,
                evaluation,
                best_net_evaluation,
                best_net_moves,
                white_move,
            )

    best_move = return_random_move(best_net_moves)

    return return_move(best_move, best_net_evaluation)


def compare_evaluations(
    move: Move,
    move_evaluation: int,
    best_evaluation: int,
    move_list: list[Move],
    white_move: bool,
) -> tuple[int, list[Move]]:
    """ 
    Compares the evaluations of a move with that of the best evaluation, and edits the move list accordingly.
    
    Returns the best evaluation and the list as well due to some bug that I can't figure out the reason behind :(
    """

    if white_move:

        # If it is white to move, we would want the greatest evaluation
        if move_evaluation == best_evaluation:
            move_list.append(move)

        elif move_evaluation > best_evaluation:
            best_evaluation = move_evaluation
            move_list = [move]

    else:

        # If black to move, we would want the least evaluation
        if move_evaluation == best_evaluation:
            move_list.append(move)

        elif move_evaluation < best_evaluation:
            move_list = [move]
            best_evaluation = move_evaluation

    return best_evaluation, move_list

def minimax_ai():
    ...
    

def get_board_evaluation(game_state: GameState) -> int:
    ...