from chess_logic import *
import random
import copy


def return_move(move: Move, evaluation) -> tuple[Move, str, int]:
    """
    Returns the move with the correct format.

    Assumes to always promote to queen for now
    """
    if not move:
        return None, "", evaluation

    if move.is_pawn_promotion:
        return move, "Q", evaluation

    return move, "", evaluation


def return_random_move(moves: list[Move]) -> Move:
    """Returns a random move from a list of moves

    Returns None if there is no move"""

    # Change the seed to make it more random
    random.seed()
    length = len(moves)

    if not length:
        return None

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


def negamax_ai(
    game_state: GameState, valid_moves: list[Move], depth: int
) -> tuple[Move, str, float]:
    """
    A negamax AI which has a much more complex evaluation function, did not make use of copy
    """

    global counter

    counter = 0

    # To hold the max score among the moves
    max_evaluation = -100000

    best_net_moves = []

    turn_multiplier = 1 if game_state.white_move else -1
    
    valid_moves = order_moves(valid_moves)

    for move in valid_moves:

        if move.is_pawn_promotion:
            game_state.make_move(move, "Q")

        else:
            game_state.make_move(move)

        next_valid_moves = game_state.get_valid_moves()
        counter += 1

        evaluation = -get_negamax_evaluation(
            game_state, next_valid_moves, depth - 1, -turn_multiplier, -100000, 100000
        )

        # Compare the evaluations, we do not need to call the function since we only check for max
        if evaluation > max_evaluation:
            max_evaluation = evaluation
            best_net_moves = [move]

        elif evaluation == max_evaluation:
            best_net_moves.append(move)

        game_state.undo_move()

    print(f"Positions searched: {counter}")
    return return_move(return_random_move(best_net_moves), max_evaluation)


def get_negamax_evaluation(
    game_state: GameState,
    valid_moves: list[Move],
    depth: int,
    turn_multiplier: int,
    alpha: float,
    beta: float,
) -> float:
    """
    Returns the evaluation of a given position using the negamax algorithm

    Alpha beta pruning used.
    """

    global counter

    if not depth:
        return turn_multiplier * get_board_evaluation(game_state, valid_moves)

    # Move ordering - find moves that are better (check and captures first)
    valid_moves = order_moves(valid_moves)

    max_evaluation = -100000

    for move in valid_moves:
        if move.is_pawn_promotion:
            game_state.make_move(move, "Q")

        else:
            game_state.make_move(move)

        next_valid_moves = game_state.get_valid_moves()
        counter += 1
        
        if game_state.in_check:
            new_depth = depth
        
        else:
            new_depth = depth - 1

        evaluation = -get_negamax_evaluation(
            game_state, next_valid_moves, new_depth, -turn_multiplier, -beta, -alpha
        )

        if evaluation > max_evaluation:
            max_evaluation = evaluation

        game_state.undo_move()

        # Pruning - as long as the eval is greater than the upper bound, we are going to choose that tree
        if max_evaluation > alpha:
            alpha = max_evaluation

        if alpha >= beta:
            break
    return max_evaluation


def get_board_evaluation(game_state: GameState, valid_moves: list[Move]) -> float:
    """
    Returns the board evaluation, with a larger number being better for white and vice versa

    Factors considered:
    1) Is the position checkmate or stalemate
    2) Material count
    """

    # If there are no valid moves, it is either checkmate or stalemate
    if not valid_moves:
        if game_state.in_check:
            return -10000 if game_state.white_move else 10000

        else:
            return 0

    if game_state.draw_log[-1].check_for_draw():
        return 0
    
    # Calculates the evaluation of the position otherwise
    peSTO_evaluation = peSTO_pst.get_board_evaluation(game_state.board)

    return peSTO_evaluation


def compare_evaluations(
    move: Move,
    move_evaluation: float,
    best_evaluation: float,
    move_list: list[Move],
    white_move: bool,
) -> tuple[float, list[Move]]:
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


def order_moves(valid_moves: list[Move]) -> list[Move]:
    """ Returns the list of valid moves based on the value of captures """
    
    sort = {
        "Q": [],
        "R": [],
        "B": [],
        "N": [],
        "p": [],
        "promotion": [],
        "None": []
    }
    
    for move in valid_moves:
        if move.is_pawn_promotion:
            sort["promotion"].append(move)
            
        elif piece_captured := move.piece_captured:
            sort[piece_captured[1]].append(move)
            
        else:
            sort["None"].append(move)
            
    return sort["promotion"] + sort["Q"] + sort["R"] + sort["B"] + sort["N"] + sort["p"] + sort["None"]
        

class peSTO_pst:

    mg_values = {"p": 82, "N": 337, "B": 365, "R": 477, "Q": 1025, "K": 0}

    eg_values = {"p": 94, "N": 281, "B": 297, "R": 512, "Q": 936, "K": 0}

    mg_pawn_table = [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [98, 134, 61, 95, 68, 126, 34, -11],
        [-6, 7, 26, 31, 65, 56, 25, -20],
        [-14, 13, 6, 21, 23, 12, 17, -23],
        [-27, -2, -5, 18, 18, 6, 10, -25],
        [-26, -4, -4, -10, 3, 3, 33, -12],
        [-35, -1, -20, -23, -15, 24, 38, -22],
        [0, 0, 0, 0, 0, 0, 0, 0],
    ]

    eg_pawn_table = [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [178, 173, 158, 134, 147, 132, 165, 187],
        [94, 100, 85, 67, 56, 53, 82, 84],
        [32, 24, 13, 5, -2, 4, 17, 17],
        [13, 9, -3, -7, -7, -8, 3, -1],
        [4, 7, -6, 1, 0, -5, -1, -8],
        [13, 8, 8, 10, 13, 0, 2, -7],
        [0, 0, 0, 0, 0, 0, 0, 0],
    ]

    mg_knight_table = [
        [-167, -89, -34, -49, 61, -97, -15, -107],
        [-73, -41, 72, 36, 23, 62, 7, -17],
        [-47, 60, 37, 65, 84, 129, 73, 44],
        [-9, 17, 19, 53, 37, 69, 18, 22],
        [-13, 4, 16, 13, 28, 19, 21, -8],
        [-23, -9, 12, 10, 19, 17, 25, -16],
        [-29, -53, -12, -3, -1, 18, -14, -19],
        [-105, -21, -58, -33, -17, -28, -19, -23],
    ]

    eg_knight_table = [
        [-58, -38, -13, -28, -31, -27, -63, -99],
        [-25, -8, -25, -2, -9, -25, -24, -52],
        [-24, -20, 10, 9, -1, -9, -19, -41],
        [-17, 3, 22, 22, 22, 11, 8, -18],
        [-18, -6, 16, 25, 16, 17, 4, -18],
        [-23, -3, -1, 15, 10, -3, -20, -22],
        [-42, -20, -10, -5, -2, -20, -23, -44],
        [-29, -51, -23, -15, -22, -18, -50, -64],
    ]

    mg_bishop_table = [
        [-29, 4, -82, -37, -25, -42, 7, -8],
        [-26, 16, -18, -13, 30, 59, 18, -47],
        [-16, 37, 43, 40, 35, 50, 37, -2],
        [-4, 5, 19, 50, 37, 37, 7, -2],
        [-6, 13, 13, 26, 34, 12, 10, 4],
        [0, 15, 15, 15, 14, 27, 18, 10],
        [4, 15, 16, 0, 7, 21, 33, 1],
        [-33, -3, -14, -21, -13, -12, -39, -21],
    ]

    eg_bishop_table = [
        [-8, -4, 7, -12, -3, -13, -4, -14],
        [-14, -21, -11, -8, -7, -9, -17, -24],
        [2, -8, 0, -1, -2, 6, 0, 4],
        [-3, 9, 12, 9, 14, 10, 3, 2],
        [-6, 3, 13, 19, 7, 10, -3, -9],
        [-12, -3, 8, 10, 13, 3, -7, -15],
        [-14, -18, -7, -1, 4, -9, -15, -27],
        [-23, -9, -23, -5, -9, -16, -5, -17],
    ]

    mg_rook_table = [
        [32, 42, 32, 51, 63, 9, 31, 43],
        [27, 32, 58, 62, 80, 67, 26, 44],
        [-5, 19, 26, 36, 17, 45, 61, 16],
        [-24, -11, 7, 26, 24, 35, -8, -20],
        [-36, -26, -12, -1, 9, -7, 6, -23],
        [-45, -25, -16, -17, 3, 0, -5, -33],
        [-44, -16, -20, -9, -1, 11, -6, -71],
        [-19, -13, 1, 17, 16, 7, -37, -26],
    ]

    eg_rook_table = [
        [13, 10, 18, 15, 12, 12, 8, 5],
        [11, 13, 13, 11, -3, 3, 8, 3],
        [7, 7, 7, 5, 4, -3, -5, -3],
        [4, 3, 13, 1, 2, 1, -1, 2],
        [3, 5, 8, 4, -5, -6, -8, -11],
        [-4, 0, -5, -1, -7, -12, -8, -16],
        [-6, -6, 0, 2, -9, -9, -11, -3],
        [-9, 2, 3, -1, -5, -13, 4, -20],
    ]

    mg_queen_table = [
        [-28, 0, 29, 12, 59, 44, 43, 45],
        [-24, -39, -5, 1, -16, 57, 28, 54],
        [-13, -17, 7, 8, 29, 56, 47, 57],
        [-27, -27, -16, -16, -1, 17, -2, 1],
        [-9, -26, -9, -10, -2, -4, 3, -3],
        [-14, 2, -11, -2, -5, 2, 14, 5],
        [-35, -8, 11, 2, 8, 15, -3, 1],
        [-1, -18, -9, 10, -15, -25, -31, -50],
    ]

    eg_queen_table = [
        [-9, 22, 22, 27, 27, 19, 10, 20],
        [-17, 20, 32, 41, 58, 25, 30, 0],
        [-20, 6, 9, 49, 47, 35, 19, 9],
        [3, 22, 24, 45, 57, 40, 57, 36],
        [-18, 28, 19, 47, 31, 34, 39, 23],
        [-16, -27, 15, 6, 9, 17, 10, 5],
        [-22, -23, -30, -16, -16, -23, -36, -32],
        [-33, -28, -22, -43, -5, -32, -20, -41],
    ]

    mg_king_table = [
        [-65, 23, 16, -15, -56, -34, 2, 13],
        [29, -1, -20, -7, -8, -4, -38, -29],
        [-9, 24, 2, -16, -20, 6, 22, -22],
        [-17, -20, -12, -27, -30, -25, -14, -36],
        [-49, -1, -27, -39, -46, -44, -33, -51],
        [-14, -14, -22, -46, -44, -30, -15, -27],
        [1, 7, -8, -64, -43, -16, 9, 8],
        [-15, 36, 12, -54, 8, -28, 24, 14],
    ]

    eg_king_table = [
        [-74, -35, -18, -18, -11, 15, 4, -17],
        [-12, 17, 14, 17, 17, 38, 23, 11],
        [10, 17, 23, 15, 20, 45, 44, 13],
        [-8, 22, 24, 27, 26, 33, 26, 3],
        [-18, -4, 21, 24, 27, 23, 9, -11],
        [-19, -3, 11, 21, 23, 16, 7, -9],
        [-27, -11, 4, 13, 14, 4, -5, -17],
        [-53, -34, -21, -11, -28, -14, -24, -43],
    ]

    mg_tables = {
        "p": mg_pawn_table,
        "N": mg_knight_table,
        "B": mg_bishop_table,
        "R": mg_rook_table,
        "Q": mg_queen_table,
        "K": mg_king_table,
    }

    eg_tables = {
        "p": eg_pawn_table,
        "N": eg_knight_table,
        "B": eg_bishop_table,
        "R": eg_rook_table,
        "Q": eg_queen_table,
        "K": eg_king_table,
    }

    game_phase_indicator = {"p": 0, "N": 1, "B": 1, "R": 2, "Q": 4, "K": 0}

    def __init__(self) -> None:
        pass

    @classmethod
    def get_square_evaluation(
        cls, square: tuple, colour: str, piece_type: str
    ) -> tuple[int, int]:
        """
        Returns the evaluation of a specific piece on a specific square

        Returns a tuple of [middle game eval, end game eval]
        """

        row, column = square

        # If it is a black piece, we need to swap the square and column to be from their perspective
        if colour == "b":
            row = 7 - row

        # Calculate middle game and endgame score
        mg_score = cls.mg_tables[piece_type][row][column] + cls.mg_values[piece_type]
        eg_score = cls.eg_tables[piece_type][row][column] + cls.eg_values[piece_type]

        return mg_score, eg_score

    @classmethod
    def get_board_evaluation(cls, board: list[list[str]]) -> float:
        """
        Returns the evaluation of the entire board

        A larger number means that its better for white and vice versa
        """

        # To keep track of which phase it is
        mg_phase = 0

        # To keep track of both side's scores
        white_mg_score = white_eg_score = 0
        black_mg_score = black_eg_score = 0

        for row in range(8):
            for column in range(8):

                # If there is a piece on the square
                if piece := board[row][column]:

                    colour, piece_type = piece
                    mg_phase += cls.game_phase_indicator[piece_type]

                    # Get the tuple of scores of the piece
                    mg_score, eg_score = cls.get_square_evaluation(
                        (row, column), colour, piece_type
                    )

                    # Adds the scores to the respective counters
                    if colour == "w":
                        white_mg_score += mg_score
                        white_eg_score += eg_score

                    else:
                        black_mg_score += mg_score
                        black_eg_score += eg_score

        if mg_phase > 24:
            mg_phase = 24

        eg_phase = 24 - mg_phase

        mg_score = white_mg_score - black_mg_score
        eg_score = white_eg_score - black_eg_score

        return (mg_score * mg_phase + eg_score * eg_phase) / 24
