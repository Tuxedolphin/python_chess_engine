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
        
        # Other useful states to hold in memory
        self.in_check = False
        self.pins = []
        self.checks = []
        
        # Keep track of coordinate of square where en passant is possible
        self.en_passant_square = ()
        
        # Keep track of castling rights
        self.current_castle_rights = CastleRights(True, True, True, True)
        self.castle_rights_log = [self.current_castle_rights]
        
        
    def make_move(self, move, promotion_type: str = "") -> None:
        """
        Makes a move given a move class, note that if it is a promotion, the proper input should be given

        Args:
            move (Move): A Move class of the move to be made
        """
        
        # Update location of pieces
        self.board[move.start_row][move.start_column] = ""
        self.board[move.end_row][move.end_column] = move.piece_moved

        self.move_log.append(move)
        
        print(f"move is: {move.get_chess_notation()}")
        
        if move.piece_moved == "wK":
            self.white_king_location = (move.end_row, move.end_column)
            
        elif move.piece_moved == "bK":
            self.black_king_location = (move.end_row, move.end_column)
        
        self.white_move = not self.white_move
        
        # If it is a pawn promotion
        if move.is_pawn_promotion:
            self.board[move.end_row][move.end_column] = move.piece_moved[0] + promotion_type
        
        # En passant
        elif move.is_en_passant:
            
            # Capture the pawn
            self.board[move.start_row][move.end_column] = ""
            
        # Check and update for squares where en passant is possible
        if move.piece_moved[1] == "p" and abs(move.start_row - move.end_row) == 2:
            
            self.en_passant_square = ((move.start_row + move.end_row) // 2, move.end_column)
        
        # Else make sure no en passant is possible
        else:
            self.en_passant_square = ()
        
        # Update of castling rights
        
        # Take into account a bool maybe, such that if both sides can't castle we stop checking for this
        
    
    def undo_move(self) -> None:
        """
        Undoes the last move
        """
        
        if self.move_log:
            move = self.move_log.pop()
            
            self.board[move.start_row][move.start_column] = move.piece_moved
            self.board[move.end_row][move.end_column] = move.piece_captured
            
            if move.piece_moved == "wK":
                self.white_king_location = (move.start_row, move.start_column)
            
            elif move.piece_moved == "bK":
                self.black_king_location = (move.start_row, move.start_column)
            
            self.white_move = not self.white_move
            
            # Undo en passant
            if move.is_en_passant:
                self.board[move.end_row][move.end_column] = ""
                self.board[move.start_row][move.end_column] = move.piece_captured
                self.en_passant_square = (move.end_row, move.end_column)
                
                print("Undone move was en passant")
            
    
    def get_valid_moves(self) -> list:
        """
        Returns all the valid moves in the current game state

        Returns:
            list: list of all valid moves
        """
        
        moves = []
        
        self.in_check, self.pins, self.checks = self.check_for_pins_checks()
        
        print(f"in check: {self.in_check}")
        print(f"pins: {self.pins}")
        print(f"checks: {self.checks}")
        
        # Getting the location of the king
        if self.white_move:
            king_row, king_column = self.white_king_location
            
        else:
            king_row, king_column = self.black_king_location
            
        if self.in_check:
            
            # If there is only 1 check, we must block the check, capture the piece, or move the king
            if len(self.checks) == 1:
                moves = self.get_all_moves()
                
                # Check if the move can block the check
                check = self.checks[0]
                piece_checking = self.board[check[0]][check[1]]
                
                valid_squares = []
                
                # If it is a knight, must move the king or capture the knight
                if piece_checking[1] == "N":
                    valid_squares.append(check)
                
                # Else, it can block the check where piece can move from king to attacking piece
                else:
                    for i in range(1, 8):
                        
                        square = (king_row + check[2] * i, king_column + check[3] * i)
                        
                        if 0 <= square[0] < self.dimensions and 0 <= square[1] < self.dimensions:
                            valid_squares.append(square)
                        else:
                            break
                        
                        # If it is the square where the piece can be captured
                        if square == (check[0], check[1]):
                            break
                        
                # Get rid of moves that don't block the check or move the king
                for move in moves.copy():
                    
                    if move.piece_moved[1] != "K":
                        
                        if not (move.end_row, move.end_column) in valid_squares:
                            moves.remove(move)
            
            # Else it is double or triple check, and the king has to move
            else:
                self.get_king_moves(king_row, king_column, moves)
        
        # If king not in check, all moves are valid moves except for pins
        else:
            moves = self.get_all_moves()
            
        return moves
        
    
    def check_for_pins_checks(self) -> tuple[bool, list, list]:
        """
        Returns a tuple for if the king is in check, the pins and the checks that are in the game state (if any)

        Returns:
            tuple: a tuple of (in check, list of pins, list of checks)
        """
        
        pins = []
        checks = []
        in_check = False
        
        if self.white_move:
            opponent_colour, turn_colour = "b", "w"
            start_row, start_column = self.white_king_location
            
        else:
            opponent_colour, turn_colour = "w", "b"
            start_row, start_column = self.black_king_location
            
        # Check for all directions, i.e. movement of queen
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1), (-1, 0), (0, -1), (1, 0), (0, 1))

        for j in range(len(directions)):
            direction = directions[j]
            possible_pin = ()
            
            # For each direction, move and check for all possible squares in direction
            for i in range(1, 8):
                counter_row = start_row + direction[0] * i
                counter_column = start_column + direction[1] * i
                
                # To make sure it is within board
                if 0 <= counter_row < 8 and 0 <= counter_column < 8:
                    
                    # If there is a piece on the specific square
                    if end_piece := self.board[counter_row][counter_column]:
                        
                        # If it is an ally piece
                        if end_piece[0] == turn_colour and end_piece[1] != "K":
                            
                            # If it is the first ally piece, it may be pinned, otherwise no pins
                            if not possible_pin:
                                possible_pin = (counter_row, counter_column, direction[0], direction[1])

                            else:
                                break
                        
                        # Else if it is an opponent's piece
                        elif end_piece[0] == opponent_colour:
                            type = end_piece[1]
                            
                            # Checking if a piece can put the king in check given its direction
                            if (0 <= j < 4 and type == "B") or (4 <= j < 8 and type == "R") or \
                                (type == "Q") or (i == 1 and type == "K") or \
                                (i == 1 and type == "p" and ((opponent_colour == "w" and j in (2, 3)) or (opponent_colour == "b" and j in (0, 1)))):
                                
                                
                                # If no piece is blocking sight, it is in check
                                if not possible_pin:
                                    in_check = True
                                    checks.append((counter_row, counter_column, direction[0], direction[1]))
                                    
                                    break
                                
                                # Else if there is a piece, it is a pin
                                else:
                                    pins.append(possible_pin)
                                    
                                    break
                                
                            else:
                                break
                            
                else:
                    break
                
        # Check for knight checks
        knight_moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        
        for move in knight_moves:
            counter_row = start_row + move[0]
            counter_column = start_column + move[1]
            
            # To make sure it is within the board
            if 0 <= counter_row < 8 and 0 <= counter_column < 8:
                if piece := self.board[counter_row][counter_column]:
                
                    # If it is a knight
                    if piece[0] == opponent_colour and piece[1] == "N":
                        in_check = True
                        checks.append((counter_row, counter_column, move[0], move[1]))
                        
        return in_check, pins, checks
    
    def king_in_check(self) -> bool:
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
        
        # For if the piece is pinned
        piece_pinned = False
        pin_direction = ()
        
        for pin in self.pins.copy():
            if pin[0] == row and pin[1] == column:
                piece_pinned = True
                pin_direction = (pin[2], pin[3])
                
                self.pins.remove(pin)
                
                # A piece can only be pinned from one direction
                break
        
        # For white pawns
        if self.white_move:
            
            # Check if square in front is empty and not pinned (but moving in direction of pin is fine)
            if not self.board[row - 1][column]:
                if not piece_pinned or pin_direction == (-1, 0):
                    moves.append(Move((row, column), (row - 1, column), self.board))
                
                    # If it is on starting row, check if the 2nd square in front is empty
                    if not self.board[row - 2][column] and row == 6:
                        moves.append(Move((row, column), (row - 2, column), self.board))
            
            # Check for captures
            
            # If can capture to left
            if column - 1 >= 0:
                
                # Check if piece that can be captured is black
                if self.board[row - 1][column - 1].startswith("b"):
                    
                    # Checking for pins
                    if not piece_pinned or pin_direction == (-1, -1):
                        moves.append(Move((row, column), (row - 1, column - 1), self.board))
                        
                # If it is empty, check if it is the square where en passant is possible
                elif (row - 1, column - 1) == self.en_passant_square:
                    if not piece_pinned or pin_direction == (-1, -1):
                        moves.append(Move((row, column), (row - 1, column - 1), self.board, True))

            # If can capture to right
            if column + 1 < self.dimensions:
                
                # Check if piece that can be captured is black
                if self.board[row - 1][column + 1].startswith("b"):
                    
                    # Check for any pins
                    if not piece_pinned or pin_direction == (-1, 1):
                        moves.append(Move((row, column), (row - 1, column + 1), self.board))
                        
                elif (row - 1, column + 1) == self.en_passant_square:
                    if not piece_pinned or pin_direction == (-1, 1):
                        moves.append(Move((row, column), (row - 1, column + 1), self.board, True))
            
        # For black pawns
        else:
            
            if not self.board[row + 1][column]:
                
                # Check for if piece is pinned/ if it can move in direction of pin
                if not piece_pinned or pin_direction == (1, 0):
                    moves.append(Move((row, column), (row + 1, column), self.board))
                
                    if not self.board[row + 2][column] and row == 1:
                        moves.append(Move((row, column), (row + 2, column), self.board))
            
            if column - 1 >= 0:
                
                if self.board[row + 1][column - 1].startswith("w"):
                    if not piece_pinned or pin_direction == (1, -1):
                        moves.append(Move((row, column), (row + 1, column - 1), self.board))
                        
                elif (row + 1, column - 1) == self.en_passant_square:
                    if not piece_pinned or pin_direction == (1, -1):
                        moves.append(Move((row, column), (row + 1, column - 1), self.board, True))

            if column + 1 < self.dimensions:
                
                if self.board[row + 1][column + 1].startswith("w"):
                    if not piece_pinned or pin_direction == (1, 1):
                        moves.append(Move((row, column), (row + 1, column + 1), self.board))
                
                elif (row + 1, column + 1) == self.en_passant_square:
                    if not piece_pinned or pin_direction == (1, 1):
                        moves.append(Move((row, column), (row + 1, column + 1), self.board, True))
    
    def get_rook_moves(self, row: int, column: int, moves: list) -> None:
        """ Appends to list all of the rook moves """
        
        piece_pinned = False
        pin_direction = ()
        
        for pin in self.pins.copy():
            if pin[0] == row and pin[1] == column:
                piece_pinned = True
                pin_direction = (pin[2], pin[3])
                
                # If it is not the queen as you also need to check for bishop diagonal for queen
                if self.board[row][column][1] != "Q":
                    self.pins.remove(pin)
           
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        opponent = "b" if self.white_move else "w"
        
        for direction in directions:
            for i in range(1, 8):
                
                # Get the maximum the rook can move
                counter_row = row + direction[0] * i
                counter_column = column + direction[1] * i
                
                # If it is still in the board
                if 0 <= counter_row < self.dimensions and 0 <= counter_column < self.dimensions:
                    
                    # If piece is not pinned/ move in direction of pin
                    if not piece_pinned or pin_direction == direction or pin_direction == (-direction[0], -direction[1]):
                    
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
        
        # To check for pinned pieces
        piece_pinned = False
        pin_direction = ()
        
        for pin in self.pins.copy():
            if pin[0] == row and pin[1] == column:
                piece_pinned = True
                pin_direction = (pin[2], pin[3])
                
                self.pins.remove(pin)
                
                break        
        
        directions = ((-1, -1), (1, -1), (1, 1), (-1, 1))
        opponent = "b" if self.white_move else "w"
        
        for direction in directions:
            for i in range(1, 8):
                
                # Get the maximum the rook bishop move
                counter_row = row + direction[0] * i
                counter_column = column + direction[1] * i
                
                # If it is still in the board
                if 0 <= counter_row < self.dimensions and 0 <= counter_column < self.dimensions:
                    
                    # If not pinned or in direction of pin
                    if not piece_pinned or pin_direction == direction or pin_direction == (-direction[0], -direction[1]):
                    
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
        
        # Check for if piece is pinned (direction doesn't matter for knight)
        piece_pinned = False
        
        for pin in self.pins.copy():
            if pin[0] == row and pin[1] == column:
                piece_pinned = True
                
                self.pins.remove(pin)
                break
        
        # All the moves that a knight can make from its position
        knight_moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        opponent = "b" if self.white_move else "w"
        
        for move in knight_moves:
            move_row = row + move[0]
            move_column = column + move[1]
            
            if 0 <= move_row < self.dimensions and 0 <= move_column < self.dimensions:
                
                # If it is not pinned
                if not piece_pinned:
                
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
        turn = "w" if self.white_move else "b"
        
        for move in king_moves:
            move_row = row + move[0]
            move_column = column + move[1]
            
            if 0 <= move_row < self.dimensions and 0 <= move_column < self.dimensions:        
                
                # If it is not self's piece (i.e. either empty or opponent piece)
                if not self.board[move_row][move_column].startswith(turn):
                    
                    # Place king on new square and check for checks
                    if turn == "w":
                        self.white_king_location = (move_row, move_column)
                    else:
                        self.black_king_location = (move_row, move_column)
                    
                    in_check, _, checks = self.check_for_pins_checks()
                        
                    if not in_check:
                        moves.append(Move((row, column), (move_row, move_column), self.board))
                    
                    # Return king back to original position
                    if turn == "w":
                        self.white_king_location = (row, column)
                    else:
                        self.black_king_location = (row, column)
        
        
class Move:

    # Dict to map standard chess notation to the list of lists and vice versa
    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}

    files_to_columns = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    columns_to_files = {v: k for k, v in files_to_columns.items()}


    def __init__(self, start: tuple, end: tuple, board: GameState, is_en_passant: bool = False) -> None:
        """
        Generates a chess move which keeps track of the move to be made, as well as
        the piece that is being moved and the piece that is being captured

        Args:
            start (tuple): row, column of initial starting square
            end (tuple): row, column of square for the piece to be moved to
            board (GameState.board): The current board
            is_en_passant (bool): Whether or not the move is an en passant
        """

        # Uncouples the tuple
        self.start_row, self.start_column = start
        self.end_row, self.end_column = end

        # Stores the piece moved and piece captured (if any)
        self.piece_moved = board[self.start_row][self.start_column]
        self.piece_captured = board[self.end_row][self.end_column]

        # A unique identifier to make it easier for comparing
        self.move = [start, end]
        
        # To keep track of if it is a pawn promotion
        self.is_pawn_promotion = ((self.piece_moved == "wp" and self.end_row == 0) or (self.piece_moved == "bp" and self.end_row == 7))
                
        # Keep track of if move is en passant
        self.is_en_passant = is_en_passant
        
        if is_en_passant:
            self.piece_captured = board[self.start_row][self.end_column]
        
        
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
        

class CastleRights():
    
    def __init__(self, white_king_side, black_king_side, white_queen_side, black_queen_side):
        
        
        self.white_king_side = white_king_side
        self.black_king_side = black_king_side
        self.white_queen_side = white_queen_side
        self.black_queen_side = black_queen_side