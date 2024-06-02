from chess_logic import *
import random
import copy
import datetime

def return_move(move: Move, evaluation) -> tuple[Move, str, int]:
    """
    Returns the move with the correct format.

    Assumes to always promote to queen for now
    """

    if move.is_pawn_promotion:
        return move, "Q", evaluation

    return move, "", evaluation


def return_random_move(moves: list[Move]) -> Move:
    """ Returns a random move from a list of moves """
    
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
    valid_moves: list,
    game_state: GameState,
    depth: int = 2,
    current_depth: int = 0,
) -> tuple[Move, str, int]:
    """
    An AI which only considers material, except that it will recursively call itself up
    to a maximum depth of "depth" ply using a minimax algorithm.
    
    No alpha beta pruning used
    """
    
    current_material = game_state.white_material - game_state.black_material
    
    # If the recursion is over, simply return a random move
    if current_depth == depth:
        return return_move(valid_moves[0], current_material)
    
    # Keeps track of the number of ply
    current_depth += 1

    # Keep track of the move which gains/ captures the most points
    best_net_evaluation = -100000 if game_state.white_move else 100000

    # Keeps track of the moves which has the max points
    best_net_moves = []
    
    # Finds the best moves for the current iteration
    for move in valid_moves:
        
        # Creates a copy of the game state so that it is not altered and gets a new evaluation
        copied_game_state = copy.deepcopy(game_state)
        copied_game_state.make_move(move)
        copied_valid_moves = copied_game_state.get_valid_moves()
        
        if not copied_valid_moves:
            continue
        
        _, _, evaluation = materialistic_minimax_ai(
            copied_valid_moves,
            copied_game_state,
            depth,
            current_depth=current_depth
        )

        if game_state.white_move:
            if evaluation > best_net_evaluation:
                best_net_evaluation = evaluation
                best_net_moves = [move]
                
        else:
            if evaluation < best_net_evaluation:
                best_net_evaluation = evaluation
                best_net_moves = [move]

        if evaluation == best_net_evaluation:
            best_net_moves.append(move)

    # If it is the last iteration, return a random move
    best_move = return_random_move(best_net_moves)

    return return_move(best_move, best_net_evaluation)