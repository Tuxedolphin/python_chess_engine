import pygame
import chess_logic
import chess_ai


WIDTH = HEIGHT = 512 # For dimensions of pieces
DIMENSION = 8 # The dimensions of a chess board
SQUARE_SIZE = HEIGHT // DIMENSION # Getting the integer size of the square
IMAGES = {}


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    screen.fill(pygame.Color("white"))
    
    game_state = chess_logic.GameState()
    load_images()
    
    status = True
    
    # Gets the square that the user has selected
    square_selected = ()
    
    # Keeps track of the movement of piece
    piece_move = []
    
    # Keeps track of all valid moves in current position
    valid_moves = game_state.get_valid_moves()
    
    # Keeps track of if a move has been made, i.e. game state has been changed
    move_made = False
    
    while status:
        for event in pygame.event.get():
            
            # If quit
            if event.type == pygame.QUIT:
                status = False
            
            # If person clicks on a piece
            elif event.type == pygame.MOUSEBUTTONDOWN:
                coordinates = pygame.mouse.get_pos()
                
                # Gets the column of row of what is selected
                column = coordinates[0] // SQUARE_SIZE
                row = coordinates[1] // SQUARE_SIZE
                
                # If user has already selected the piece, unselect the piece
                if square_selected == (row, column):
                    square_selected = ()
                    piece_move = []
                
                # Else, update the square that is selected, keep track of selected square
                else:
                    square_selected = (row, column)
                    piece_move.append(square_selected)
                
                # If it is the user's second click, move the piece if a piece was selected
                if len(piece_move) == 2:
                    
                    # If no piece was selected, clear selection
                    if not game_state.board[piece_move[0][0]][piece_move[0][1]]:
                        piece_move.pop(0)
                    
                    else:
                        
                        move = chess_logic.Move(piece_move[0], piece_move[1], game_state.board)
                        
                        # If move is valid, make move
                        if move in valid_moves:
                            game_state.make_move(move)
                            move_made = True
                            
                            square_selected = ()
                            piece_move = []
                                
                        # Else deselect
                        else:
                            square_selected = ()
                            piece_move = []
            
            # If person presses a key
            elif event.type == pygame.KEYDOWN:
                
                # If left arrow was pressed, undo move
                if event.key == pygame.K_LEFT:
                    game_state.undo_move()
                    move_made = True
        
        # IF move has been made, generate a list of all the valid moves    
        if move_made:
            valid_moves = game_state.get_valid_moves()
            print(f"valid moves: {[move.get_chess_notation() for move in valid_moves]}")
            move_made = False
        
        draw_board(screen, game_state)    
        clock.tick(30)
        pygame.display.flip()
        

def load_images() -> None:
    """
    Load the images from the images folder, storing it in the global IMAGES dict
    """
    
    pieces = ["bR", "bN", "bB", "bQ", "bK", "bp", "wR", "wN", "wB", "wQ", "wK", "wp"]
    
    # Loads all the images to the respective key in the dictionary
    for piece in pieces:
        
        IMAGES[piece] = pygame.transform.scale(pygame.image.load(f"images/{piece}.png"), (SQUARE_SIZE, SQUARE_SIZE))
        

def draw_board(screen: pygame.display, game_state: chess_logic.GameState) -> None:
    """
    Draws the board that gets displayed in pygame

    Args:
        screen (pygame.display): The screen for the board and pieces to be displayed on
        game_state (list): The current game state
    """
    draw_squares(screen)
    draw_pieces(screen, game_state.board)


def draw_squares(screen: pygame.display) -> None:
    """
    Draws the squares on the game board

    Args:
        screen (pygame.display): The display for the board to be drawn on
    """
    
    # Defining a colour dict for which colours belongs to the light and dark squares
    colours = {
        "light": pygame.Color(231, 215, 178),
        "dark": pygame.Color(174, 136, 101)
    }
    
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            if (row + column) % 2:
                colour = colours["dark"]
            
            else:
                colour = colours["light"]
                
            pygame.draw.rect(screen, colour, pygame.Rect(column * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    
def draw_pieces(screen: pygame.display, board: chess_logic.GameState) -> None:
    """
    Draws the pieces on the board given the game state

    Args:
        screen (pygame.display): The screen to be drawn on
        board (chess_logic.GameState.board): The current game state, which includes the placement of all the pieces
    """

    for row in range(DIMENSION):
        for column in range(DIMENSION):
            piece = board[row][column]
            
            if piece:
                screen.blit(IMAGES[piece], pygame.Rect(column * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

if __name__ == "__main__":
    main()