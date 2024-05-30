import pygame
import chess_logic
import chess_ai


WIDTH = HEIGHT = 512  # For dimensions of pieces
DIMENSION = 8  # The dimensions of a chess board
SQUARE_SIZE = HEIGHT // DIMENSION  # Getting the integer size of the square
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

    # If the move should be animated
    animate = False

    # Whether or not the game has ended
    game_over = False

    while status:
        for event in pygame.event.get():

            # If quit
            if event.type == pygame.QUIT:
                status = False

            # If person clicks on a piece
            elif event.type == pygame.MOUSEBUTTONDOWN:

                if game_over:
                    continue

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

        # IF move has been made, generate a list of all the valid moves
        if move_made:
            if animate:
                animate_moves(game_state.move_log[-1], screen, game_state.board, clock)

            valid_moves = game_state.get_valid_moves()
            print(f"valid moves: {[move.get_chess_notation() for move in valid_moves]}")
            move_made = False

            # Test for checkmate and stalemate
            if not valid_moves:
                game_over = True

        if game_over:
            winner = {False: "white", True: "black"}

            (
                draw_text(
                    screen, f"Checkmate, {winner[game_state.white_move]} won!"
                )
                if game_state.in_check
                else draw_text(screen, "Stalemate")
            )
            pygame.display.update()
            clock.tick(10)
        
        else:
            draw_board(screen, game_state, valid_moves, square_selected)
            clock.tick(30)
            pygame.display.flip()


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
) -> None:
    """
    Draws the board that gets displayed in pygame

    Args:
        screen (pygame.display): The screen for the board and pieces to be displayed on
        game_state (chess_logic.GameState): The current game state
        valid_moves (list): List of valid moves in current position
        square_selected (tuple): The square selected by the user
    """
    draw_squares(screen)
    move_highlighting(screen, game_state, valid_moves, square_selected)
    draw_pieces(screen, game_state.board)


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
    frame_count = 12

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


def draw_text(screen: pygame.display, text: str) -> None:
    """Draws a text onto the screen"""

    print("Draw text is called with text: " + text)

    font = pygame.font.SysFont("arial", 32, True, False)
    text_object = font.render(text, True, pygame.Color("black"), pygame.Color("white"))
    text_location = pygame.Rect(0, 0, WIDTH, HEIGHT).move(
        WIDTH / 2 - (text_object.get_width() / 2),
        HEIGHT / 2 - (text_object.get_height() / 2),
    )
    screen.blit(text_object, text_location)

if __name__ == "__main__":
    main()
