import pygame
import sys
from python_chess import chess_logic
from python_chess import chess_ai


WIDTH = HEIGHT = 512  # For dimensions of board
MOVE_LOG_WIDTH = 250  # For dimensions of move log window
DIMENSION = 8  # The dimensions of a chess board
SQUARE_SIZE = HEIGHT // DIMENSION  # Getting the integer size of the square
IMAGES = {}
X_CENTER = (WIDTH + MOVE_LOG_WIDTH) // 2  # Gets the horizontal center of the screen
Y_CENTER = HEIGHT // 2  # Gets the vertical center of the screen

# Integers corresponding to the AIs
AI = {
    1: chess_ai.random_move_ai,
    2: chess_ai.simple_materialistic_ai,
    3: chess_ai.materialistic_minimax_ai,
    4: chess_ai.negamax_ai,
}

pygame.init()  # Initialise pygame


def main() -> None:
    
    # Default AI is the negamax AI at depth 3 ply
    global ai
    global depth
    ai, depth = 4, 3
    
    screen = pygame.display.set_mode((WIDTH + MOVE_LOG_WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    screen.fill(pygame.Color("white"))

    pygame.display.set_caption("Menu")
    screen.fill(pygame.Color("white"))

    menu_font = pygame.font.SysFont("arial", 30, False, False)
    menu_text = menu_font.render("Main Menu", True, pygame.Color("black"))

    menu_text_rect = menu_text.get_rect()
    menu_text_rect.center = (X_CENTER, Y_CENTER - 180)

    play_button = Button(
        None,
        (X_CENTER, Y_CENTER - 75),
        "PLAY",
        menu_font,
        pygame.Color("black"),
        pygame.Color("gray"),
    )
    options_button = Button(
        None,
        (X_CENTER, Y_CENTER + 25),
        "OPTIONS",
        menu_font,
        pygame.Color("black"),
        pygame.Color("gray"),
    )
    quit_button = Button(
        None,
        (X_CENTER, Y_CENTER + 125),
        "QUIT",
        menu_font,
        pygame.Color("black"),
        pygame.Color("gray"),
    )

    while True:
        menu_mouse_pos = pygame.mouse.get_pos()
        screen.blit(menu_text, menu_text_rect)

        # Updates the button should the user hover over it
        for button in [play_button, options_button, quit_button]:
            button.change_colour(menu_mouse_pos)
            button.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_button.check_for_input(menu_mouse_pos):
                    play_screen(screen, clock)

                elif options_button.check_for_input(menu_mouse_pos):
                    options_screen(screen, clock)

                elif quit_button.check_for_input(menu_mouse_pos):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()


def options_screen(screen, clock) -> None:
    """ The options menu, where users choose the AI and depth """
    
    pygame.display.set_caption("Options")
    options_font = pygame.font.SysFont("arial", 25, False, False)
    back_button = Button(None, (X_CENTER, HEIGHT - 30), "Back", options_font, pygame.Color("black"), pygame.Color("gray"))
    
    while True:
        mouse_pos = pygame.mouse.get_pos()
        
        screen.fill(pygame.Color("white"))
                
        back_button.change_colour(mouse_pos)
        back_button.update(screen)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.check_for_input(mouse_pos):
                    main()
            
        pygame.display.update()


class Button:

    def __init__(
        self,
        image,
        pos,
        text_input,
        font,
        base_colour,
        hovering_colour,
        background_color=pygame.Color("white"),
    ) -> None:
        """Initialise the button class with the basic criteria"""
        self.image = image
        self.x_pos = pos[0]
        self.y_pos = pos[1]
        self.font = font
        self.base_colour, self.hovering_colour = base_colour, hovering_colour
        self.text_input = text_input
        self.text = self.font.render(self.text_input, True, self.base_colour)
        if not self.image:
            self.image = self.text
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
        self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))
        self.background_colour = background_color

    def update(self, screen) -> None:
        """Places text/ image on screen"""
        if self.image:
            screen.blit(self.image, self.rect)
        pygame.draw.rect(
            screen,
            self.background_colour,
            self.text_rect.inflate((20, 10)),
            border_radius=3,
        )
        screen.blit(self.text, self.text_rect)

    def check_for_input(self, position) -> bool:
        """Checks if the user has clicked on the button"""

        return position[0] in range(self.rect.left, self.rect.right) and position[
            1
        ] in range(self.rect.top, self.rect.bottom)

    def change_colour(self, position) -> None:
        """Changes colour of the button if the user is hovering over the button"""
        if self.check_for_input(position):
            self.text = self.font.render(self.text_input, True, self.hovering_colour)
        else:
            self.text = self.font.render(self.text_input, True, self.base_colour)


def play_screen(screen: pygame.display, clock: pygame.time) -> None:
    """The main game screen of the application"""

    pygame.display.set_caption("Play Chess")

    game_state = chess_logic.GameState()
    load_images()

    # The font of the move log
    move_log_font = pygame.font.SysFont("arial", 15, False, False)

    # To keep track of how much the user has scrolled the move log
    global delta_y
    delta_y = 0

    # Gets the square that the user has selected
    square_selected = ()

    # Keeps track of the movement of piece
    piece_move = []

    # Keeps track of all valid moves in current position
    valid_moves = game_state.get_valid_moves()

    # Keeps track of if a move has been made, i.e. game state has been changed
    move_made = False

    # If the move should be animated
    animate = False

    # Whether or not the game has ended
    game_over = False

    # Keeps track of if player is playing white and black
    player_white, player_black = True, False
    
    button_pressed = False

    while True:

        is_human_turn = (game_state.white_move and player_white) or (
            not game_state.white_move and player_black
        )

        coordinates = pygame.mouse.get_pos()

        for event in pygame.event.get():

            # If quit
            if event.type == pygame.QUIT:
                sys.exit()

            # If user is scrolling
            elif event.type == pygame.MOUSEWHEEL:
                x_coordinate, _ = pygame.mouse.get_pos()

                # If user is scrolling at the move log area, scroll the area
                if x_coordinate // SQUARE_SIZE >= 8:
                    delta_y += event.y

            # If person clicks somewhere
            elif event.type == pygame.MOUSEBUTTONDOWN:
                
                button_pressed = True
                
                if game_over or not is_human_turn:
                    continue

                # Gets the column of row of what is selected
                column = coordinates[0] // SQUARE_SIZE
                row = coordinates[1] // SQUARE_SIZE

                # If user has already selected the piece, unselect the piece
                if square_selected == (row, column) or column >= 8:
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

                    # Else if player selected another one of his pieces
                    elif game_state.board[piece_move[1][0]][
                        piece_move[1][1]
                    ].startswith("w" if game_state.white_move else "b"):
                        piece_move.pop(0)

                    else:

                        move = chess_logic.Move(
                            piece_move[0], piece_move[1], game_state.board
                        )

                        # If move is valid, make move
                        for i in range(len(valid_moves)):
                            if move == valid_moves[i]:

                                promotion_piece = ""

                                # If it is a pawn promotion, prompt user for which piece
                                if move.is_pawn_promotion:
                                    promotion_piece = input(
                                        "Piece to be promoted (Q, N, B, R): "
                                    )

                                    # TODO: add GUI for this input

                                game_state.make_move(valid_moves[i], promotion_piece)

                                move_made = True
                                animate = True

                                square_selected = ()
                                piece_move = []

                        # If no moves made as it is illegal, deselect
                        if not move_made:
                            square_selected = ()
                            piece_move = []

            # If person presses a key
            elif event.type == pygame.KEYDOWN:

                # If left arrow was pressed, undo move
                if event.key == pygame.K_LEFT:
                    game_state.undo_move()
                    move_made = True
                    animate = False
                    game_over = False

                # If r button is pressed, reset the board
                elif event.key == pygame.K_PAGEDOWN:
                    game_state = chess_logic.GameState()
                    valid_moves = game_state.get_valid_moves()
                    square_selected = ()
                    piece_move = []
                    move_made = False
                    animate = False
                    game_over = False

        # Calls the required chess engine
        if not game_over and not is_human_turn:
            ai_move, ai_promotion_type, evaluation = chess_ai.negamax_ai(
                game_state, valid_moves, depth=3
            )
            game_state.make_move(ai_move, ai_promotion_type)
            print(f"move:{ai_move.get_chess_notation()}, evaluation: {evaluation}")

            move_made = True
            animate = True

        # If move has been made, generate a list of all the valid moves
        if move_made:
            if animate:
                animate_moves(game_state.move_log[-1], screen, game_state.board, clock)

            valid_moves = game_state.get_valid_moves()
            move_made = False

            # Test for checkmate and stalemate
            if not valid_moves or game_state.draw_log[-1].check_for_draw():
                game_over = True

        if game_over:

            if game_state.draw_log[-1].check_for_draw():
                draw_endgame_text(screen, f"Draw!")

            else:
                winner = {False: "white", True: "black"}

                (
                    draw_endgame_text(
                        screen, f"Checkmate, {winner[game_state.white_move]} won!"
                    )
                    if game_state.in_check
                    else draw_endgame_text(screen, "Stalemate")
                )
            pygame.display.update()
            clock.tick(10)

        else:
            draw_board(
                screen,
                game_state,
                valid_moves,
                square_selected,
                move_log_font,
                coordinates,
                button_pressed
            )
            clock.tick(30)
            pygame.display.flip()
            
        button_pressed = False


def move_highlighting(
    screen: pygame.display,
    game_state: chess_logic.GameState,
    valid_moves: list[chess_logic.Move],
    square_selected: tuple,
) -> None:
    """
    Highlights squares of the piece selected and where it can move to

    Args:
        screen (pygame.display): The screen where the pieces and boards are displayed on
        game_state (chess_logic.GameState): The current game state
        valid_moves (list[chess_logic.Move]): A list of the valid moves in the current position
        square_selected (tuple): The square selected by the user
    """

    if square_selected:
        row, column = square_selected

        # Make sure the piece selected is their own piece
        if game_state.board[row][column].startswith(
            "w" if game_state.white_move else "b"
        ):

            # Highlight the selected square by setting a transparent layer
            surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
            surface.fill(pygame.Color("blue"))
            surface.set_alpha(100)
            screen.blit(surface, (column * SQUARE_SIZE, row * SQUARE_SIZE))

            # Highlight the moves
            surface.fill(pygame.Color("red"))
            for move in valid_moves:
                if move.start_row == row and move.start_column == column:
                    screen.blit(
                        surface,
                        (move.end_column * SQUARE_SIZE, move.end_row * SQUARE_SIZE),
                    )

    if game_state.move_log:

        # Highlight the last move
        last_move = game_state.move_log[-1]
        surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
        surface.set_alpha(100)
        surface.fill(pygame.Color("yellow"))

        for square in last_move.move:
            row, column = square
            screen.blit(surface, (column * SQUARE_SIZE, row * SQUARE_SIZE))


def load_images() -> None:
    """
    Load the images from the images folder, storing it in the global IMAGES dict
    """

    pieces = ["bR", "bN", "bB", "bQ", "bK", "bp", "wR", "wN", "wB", "wQ", "wK", "wp"]

    # Loads all the images to the respective key in the dictionary
    for piece in pieces:

        IMAGES[piece] = pygame.transform.scale(
            pygame.image.load(f"images/{piece}.png"), (SQUARE_SIZE, SQUARE_SIZE)
        )


def draw_board(
    screen: pygame.display,
    game_state: chess_logic.GameState,
    valid_moves: list,
    square_selected: tuple,
    move_log_font: str,
    mouse_pos: tuple,
    button_pressed: bool,
) -> None:
    """
    Draws the board that gets displayed in pygame

    Args:
        screen (pygame.display): The screen for the board and pieces to be displayed on
        game_state (chess_logic.GameState): The current game state
        valid_moves (list): List of valid moves in current position
        square_selected (tuple): The square selected by the user
        move_log_font(str): Font of the move log
    """

    draw_squares(screen)
    move_highlighting(screen, game_state, valid_moves, square_selected)
    draw_pieces(screen, game_state.board)
    draw_move_log(screen, game_state, move_log_font, mouse_pos, button_pressed,)


def draw_squares(screen: pygame.display) -> None:
    """
    Draws the squares on the game board

    Args:
        screen (pygame.display): The display for the board to be drawn on
    """

    # Defining a colour dict for which colours belongs to the light and dark squares
    global colours
    colours = {
        "light": pygame.Color(231, 215, 178),
        "dark": pygame.Color(174, 136, 101),
    }

    for row in range(DIMENSION):
        for column in range(DIMENSION):
            if (row + column) % 2:
                colour = colours["dark"]

            else:
                colour = colours["light"]

            pygame.draw.rect(
                screen,
                colour,
                pygame.Rect(
                    column * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE
                ),
            )


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
                screen.blit(
                    IMAGES[piece],
                    pygame.Rect(
                        column * SQUARE_SIZE,
                        row * SQUARE_SIZE,
                        SQUARE_SIZE,
                        SQUARE_SIZE,
                    ),
                )


def draw_move_log(
    screen: pygame.display,
    game_state: chess_logic.GameState,
    move_log_font: str,
    mouse_pos: tuple,
    button_pressed: bool,
) -> None:
    """Draws the move log onto the screen"""

    # Draws a background to hold the move log
    move_log_rect = pygame.Rect(WIDTH, 0, MOVE_LOG_WIDTH, HEIGHT)
    pygame.draw.rect(screen, pygame.Color("black"), move_log_rect)

    # To hold the move log
    move_log = game_state.move_log
    move_texts = [move.get_pgn_chess_notation() for move in move_log]

    # Padding and line spacing for the moves
    padding = 5
    line_spacing = 17
    button_y_pos = 25
    
    global delta_y
    delta_y = 0 if delta_y < 0 else delta_y * 10
    
    # x, y location of each text
    text_x = padding
    text_y = padding - line_spacing - delta_y + button_y_pos * 2

    for i, move_text in enumerate(move_texts):

        if not i % 2:
            move_text = f"{int((i / 2) + 1)}. {move_text}"
            text_y += line_spacing

            text_x = padding

        else:
            text_x += 100

        text_object = move_log_font.render(move_text, 0, pygame.Color("white"))
        text_location = move_log_rect.move(text_x, text_y)
        screen.blit(text_object, text_location)
    
    rect = pygame.Rect(WIDTH, 0, MOVE_LOG_WIDTH, button_y_pos * 2)
    pygame.draw.rect(screen, (0, 0, 0), rect)

    back_font = pygame.font.SysFont("arial", 20, False, False)
    back_button = Button(
        None,
        ((WIDTH + MOVE_LOG_WIDTH // 2), button_y_pos),
        "Back",
        back_font,
        pygame.Color("white"),
        pygame.Color("gray"),
        pygame.Color("#282828"),
    )

    if button_pressed:
        if back_button.check_for_input(mouse_pos):
            main()
    
    back_button.change_colour(mouse_pos)
    back_button.update(screen)


def animate_moves(
    move: chess_logic.Move,
    screen: pygame.display,
    board: chess_logic.GameState,
    clock: pygame.time.Clock,
) -> None:
    """Animates the move"""

    global colours
    square_size = SQUARE_SIZE

    dR = move.end_row - move.start_row
    dC = move.end_column - move.start_column
    frame_count = 13

    for frame in range(frame_count + 1):
        row, column = (
            move.start_row + dR * frame / frame_count,
            move.start_column + dC * frame / frame_count,
        )
        draw_squares(screen)
        draw_pieces(screen, board)

        # Erase piece that from its ending square
        colour = colours["dark" if (move.end_row + move.end_column) % 2 else "light"]
        end_square = pygame.Rect(
            move.end_column * square_size,
            move.end_row * square_size,
            square_size,
            square_size,
        )
        pygame.draw.rect(screen, colour, end_square)

        # Draw the piece that was captured back onto the square
        if move.piece_captured:
            if move.is_en_passant:
                en_passant_row = (
                    (move.end_row - 1)
                    if move.piece_moved[0] == "b"
                    else (move.end_row + 1)
                )

                end_square = pygame.Rect(
                    move.end_column * square_size,
                    en_passant_row * square_size,
                    square_size,
                    square_size,
                )
            screen.blit(IMAGES[move.piece_captured], end_square)

        # If the move is a castle, need to animate the rook as well
        if move.king_side_castle:

            # Erasing the rook from its end square
            end_square_castle = pygame.Rect(
                (move.end_column - 1) * square_size,
                move.end_row * square_size,
                square_size,
                square_size,
            )
            colour_castle = colours["light" if colour == colours["dark"] else "dark"]
            pygame.draw.rect(screen, colour_castle, end_square_castle)

            # Animating the rook
            dC_castle = (move.end_column - 1) - (move.end_column + 1)
            column_castle = (move.end_column + 1) + dC_castle * frame / frame_count
            screen.blit(
                IMAGES[move.piece_moved[0] + "R"],
                pygame.Rect(
                    column_castle * square_size,
                    row * square_size,
                    square_size,
                    square_size,
                ),
            )

        elif move.queen_side_castle:
            end_square_castle = pygame.Rect(
                (move.end_column + 1) * square_size,
                move.end_row * square_size,
                square_size,
                square_size,
            )
            colour_castle = colours["light" if colour == colours["dark"] else "dark"]
            pygame.draw.rect(screen, colour_castle, end_square_castle)

            dC_castle = (move.end_column + 1) - (move.end_column - 2)
            column_castle = (move.end_column - 2) + dC_castle * frame / frame_count
            screen.blit(
                IMAGES[move.piece_moved[0] + "R"],
                pygame.Rect(
                    column_castle * square_size,
                    row * square_size,
                    square_size,
                    square_size,
                ),
            )

        # Draw the moving piece
        screen.blit(
            IMAGES[move.piece_moved],
            pygame.Rect(
                column * square_size, row * square_size, square_size, square_size
            ),
        )

        pygame.display.flip()
        clock.tick(60)


def draw_endgame_text(screen: pygame.display, text: str) -> None:
    """Draws a text onto the screen"""

    font = pygame.font.SysFont("arial", 32, True, False)
    text_object = font.render(text, True, pygame.Color("black"), pygame.Color("white"))
    text_location = pygame.Rect(0, 0, WIDTH, HEIGHT).move(
        WIDTH / 2 - (text_object.get_width() / 2),
        HEIGHT / 2 - (text_object.get_height() / 2),
    )
    screen.blit(text_object, text_location)


if __name__ == "__main__":
    main()
