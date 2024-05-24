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
        
        # Dimensions of a board
        self.dimensions = 8
        
        # Keep track of the kings' location
        self.white_king_location = (7, 4)
        self.black_king_location = (0, 4)
        
        
    def make_move(self, move) -> None:
        """
        Makes a move given a move class

        Args:
            move (Move): A Move class of the move to be made
        """
        
        self.board[move.start_row][move.start_column] = ""
        self.board[move.end_row][move.end_column] = move.piece_moved

        self.move_log.append(move)
        
        if move.piece_moved == "wK":
            self.white_king_location = (move.end_row, move.end_column)
            
        elif move.piece_moved == "bK":
            self.black_king_location = (move.end_row, move.end_column)
        
        self.white_move = not self.white_move
        
    
    def undo_move(self) -> None:
        """
        Undoes the last move
        """
        
        if len(self.move_log):
            move = self.move_log.pop()
            
            self.board[move.start_row][move.start_column] = move.piece_moved
            self.board[move.end_row][move.end_column] = move.piece_captured
            
            if move.piece_moved == "wK":
                self.white_king_location = (move.start_row, move.start_column)
            
            elif move.piece_moved == "bK":
                self.black_king_location = (move.start_row, move.start_column)
            
            self.white_move = not self.white_move
            
    
    def get_valid_moves(self) -> list:
        """
        Returns all the valid moves in the current game state

        Returns:
            list: list of all valid moves
        """
        
        return self.get_all_moves()
        
    
    def in_check(self) -> bool:
        """ Returns bool of if the current turn's player is in check """
        
        if self.white_move:
            return self.square_attacked(self.white_king_location)

        else:
            return self.square_attacked(self.black_king_location)
    
    
    def square_attacked(self, square: tuple) -> bool:
        """ Returns bool of if the square is under attack by opponent """
        
        # Switch turns to get the opponents turns
        self.white_move = not self.white_move
        opponents_moves = self.get_all_moves()
        self.white_move = not self.white_move
        
        for move in opponents_moves:
            
            # If the opponent can attack the square
            if move.end_row == square[0] and move.end_column == square[1]:
                return True
        
        return False
        
    def get_all_moves(self) -> list:
        """
        Returns all moves in current game state (without considering checks)

        Returns:
            list: list of all moves
        """
        
        moves = []
        
        # Setting a variable to hold who's turn it is
        turn = "w" if self.white_move else "b"
        
        # Iterate through all the pieces to determine which pieces belong to the player's turn
        for row in range(self.dimensions):
            for column in range(self.dimensions):
                
                if colour_piece := self.board[row][column]:
                    
                    if turn == colour_piece[0]:
                        
                        match colour_piece[1]:
                        
                        # How each piece moves
                            case "p":
                                self.get_pawn_moves(row, column, moves)
                            
                            case "R":
                                self.get_rook_moves(row, column, moves)
                                
                            case "B":
                                self.get_bishop_moves(row, column, moves)
                                
                            case "N":
                                self.get_knight_moves(row, column, moves)
                                
                            case "Q":
                                self.get_queen_moves(row, column, moves)
                                
                            case "K":
                                self.get_king_moves(row, column, moves)
                
        return moves

    def get_pawn_moves(self, row: int, column: int, moves: list) -> None:
        """ Appends to list all the pawn moves """
        
        # For white pawns
        if self.white_move:
            
            # Check if square in front is empty
            if not self.board[row - 1][column]:
                moves.append(Move((row, column), (row - 1, column), self.board))
                
                # If it is on starting row, check if the 2nd square in front is empty
                if not self.board[row - 2][column] and row == 6:
                    moves.append(Move((row, column), (row - 2, column), self.board))
            
            # Check for captures
            
            # If can capture to left
            if column - 1 >= 0:
                
                # Check if piece that can be captured is black
                if self.board[row - 1][column - 1].startswith("b"):
                    moves.append(Move((row, column), (row - 1, column - 1), self.board))

            # If can capture to right
            if column + 1 < self.dimensions:
                
                # Check if piece that can be captured is white
                if self.board[row - 1][column + 1].startswith("b"):
                    moves.append(Move((row, column), (row - 1, column + 1), self.board))
            
        # For black pawns
        else:
            
            if not self.board[row + 1][column]:
                moves.append(Move((row, column), (row + 1, column), self.board))
                
                if not self.board[row + 2][column] and row == 1:
                    moves.append(Move((row, column), (row + 2, column), self.board))
            
            if column - 1 >= 0:
                
                if self.board[row + 1][column - 1].startswith("w"):
                    moves.append(Move((row, column), (row + 1, column - 1), self.board))

            if column + 1 < self.dimensions:
                
                if self.board[row + 1][column + 1].startswith("w"):
                    moves.append(Move((row, column), (row + 1, column + 1), self.board))   
    
    def get_rook_moves(self, row: int, column: int, moves: list) -> None:
        """ Appends to list all of the rook moves """
        
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        opponent = "b" if self.white_move else "w"
        
        for direction in directions:
            for i in range(1, 8):
                
                # Get the maximum the rook can move
                counter_row = row + direction[0] * i
                counter_column = column + direction[1] * i
                
                # If it is still in the board
                if 0 <= counter_row < self.dimensions and 0 <= counter_column < self.dimensions:
                    
                    # If there is a piece
                    if piece := self.board[counter_row][counter_column]:
                        
                        # If it is an enemy piece
                        if piece.startswith(opponent):
                            moves.append(Move((row, column), (counter_row, counter_column), self.board))   
                        break
                    
                    # Else if it is an empty square    
                    else:
                        moves.append(Move((row, column), (counter_row, counter_column), self.board))
    
                else:
                    break
    
    def get_bishop_moves(self, row: int, column: int, moves: list) -> None: 
        """ Appends to list all of the bishop moves """
        
        directions = ((-1, -1), (1, -1), (1, 1), (-1, 1))
        opponent = "b" if self.white_move else "w"
        
        for direction in directions:
            for i in range(1, 8):
                
                # Get the maximum the rook bishop move
                counter_row = row + direction[0] * i
                counter_column = column + direction[1] * i
                
                # If it is still in the board
                if 0 <= counter_row < self.dimensions and 0 <= counter_column < self.dimensions:
                    
                    # If there is a piece
                    if piece := self.board[counter_row][counter_column]:
                        
                        # If it is an enemy piece
                        if piece.startswith(opponent):
                            moves.append(Move((row, column), (counter_row, counter_column), self.board))   
                        break
                    
                    # Else if it is an empty square    
                    else:
                        moves.append(Move((row, column), (counter_row, counter_column), self.board))
    
                else:
                    break
        
    
    def get_knight_moves(self, row: int, column: int, moves: list) -> None:
        """ Appends to list all of the knight moves """
        
        # All the moves that a knight can make from its position
        knight_moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        opponent = "b" if self.white_move else "w"
        
        for move in knight_moves:
            move_row = row + move[0]
            move_column = column + move[1]
            
            if 0 <= move_row < self.dimensions and 0 <= move_column < self.dimensions:
                
                # If there is a piece
                if piece := self.board[move_row][move_column]:
                    if piece.startswith(opponent):
                        moves.append(Move((row, column), (move_row, move_column), self.board))

                # Else if it is an empty square
                else:
                    moves.append(Move((row, column), (move_row, move_column), self.board))
    
    def get_queen_moves(self, row: int, column: int, moves: list) -> None:
        """ Appends to list all of the queen moves """
        
        self.get_rook_moves(row, column, moves)
        self.get_bishop_moves(row, column, moves)
        
    
    def get_king_moves(self, row: int, column: int, moves: list) -> None:
        """ Appends to list all of the king moves """
        
        # All the moves that a king can make from its position
        king_moves = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, 0), (1, -1), (1, 1))
        opponent = "b" if self.white_move else "w"
        
        for i in range(8):
            move_row = row + king_moves[i][0]
            move_column = column + king_moves[i][1]
            
            if 0 <= move_row < self.dimensions and 0 <= move_column < self.dimensions:
                
                # If there is a piece
                if piece := self.board[move_row][move_column]:
                    if piece.startswith(opponent):
                        moves.append(Move((row, column), (move_row, move_column), self.board))

                # Else if it is an empty square
                else:
                    moves.append(Move((row, column), (move_row, move_column), self.board))
        
        
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

        # To make it easier for comparing
        self.move = [start, end]


    def __eq__(self, other):
        if isinstance(other, Move):
            return self.move == other.move
    

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
        
    