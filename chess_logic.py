class GameState:
    """
    Class for storing all the information about state of board
    """

    def __init__(self) -> None:

        # Generates a list of list which represents the initial board state
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
        ]

        # Keeps track of who's turn to move
        self.white_move = True

        # List to keep track of moves made
        self.move_log = []
        
        
    def make_move(self, move) -> None:
        """
        Makes a move given a move class

        Args:
            move (Move): A Move class of the move to be made
        """
        
        self.board[move.start_row][move.start_column] = ""
        self.board[move.end_row][move.end_column] = move.piece_moved

        self.move_log.append(move)
        
        self.white_move = not self.white_move

class Move:

    # Dict to map standard chess notation to the list of lists and vice versa
    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}

    files_to_columns = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    columns_to_files = {v: k for k, v in files_to_columns.items()}


    def __init__(self, start: tuple, end: tuple, board: GameState) -> None:
        """
        Generates a chess move which keeps track of the move to be made, as well as
        the piece that is being moved and the piece that is being captured

        Args:
            start (tuple): row, column of initial starting square
            end (tuple): row, column of square for the piece to be moved to
            board (GameState.board): The current board
        """

        # Uncouples the couple
        self.start_row, self.start_column = start
        self.end_row, self.end_column = end

        # Stores the piece moved and piece captured (if any)
        self.piece_moved = board[self.start_row][self.start_column]
        self.piece_captured = board[self.end_row][self.end_column]


    def get_chess_notation(self) -> str:
        """
        Returns a string of chess notation of square piece moved from to moved to

        Returns:
            str: the chess notation of the move
        """
        return self.get_rank_file(self.start_row, self.start_column) + self.get_rank_file(self.end_row, self.end_column)
        
    
    def get_rank_file(self, row: int, column: int) -> str:
        """
        Returns the chess notation of the required row and column

        Args:
            row (int): Row in chess board
            column (int): Column in chess board

        Returns:
            str: Chess notation of the coordinate
        """
        return self.columns_to_files[column] + self.rows_to_ranks[row]
        
    