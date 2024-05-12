import chess
from chess import Move
import chess.polyglot


def main():
    board = chess.Board()
    
    # While the game has not ended
    while board.is_game_over():

        # While in opening book
        
            # Get opponent move
            
            # Search for best move and play it
            
        # When out of opening, continue search


def get_from_opening(board: chess.Board, reader: chess.polyglot.MemoryMappedReader) -> chess.:
    """ Returns the most played move according to opening book"""
    return reader.get(board)


def opening_search_for_best(board):
    with chess.polyglot.MemoryMappedReader("/Ranomi 1.4.bin") as reader:
    move = get_from_opening(board, reader)
    

def search_for_best(board: chess.Board):
    # Look through each move
    for move in board.legal_moves:
        
    
    #
        

def get_evaluation(board: chess.Board) -> float:
    """
    Function to return the evaluation of any board state

    Args:
        board (chess.Board): The current position of the board to be analysed

    Returns:
        float: The evaluation
    """
    
    # Gets the set of squares for each of the pieces on either sides from board
    wKing = board.pieces(chess.KING, True)
    bKing = board.pieces(chess.KING, False)
    
    wKnight = board.pieces(chess.KNIGHT, True)
    bKnight = board.pieces(chess.KNIGHT, False)
    
    wBishop = board.pieces(chess.BISHOP, True)
    bBishop = board.pieces(chess.BISHOP, False)
    
    wRook = board.pieces(chess.ROOK, True)
    bRook = board.pieces(chess.ROOK, False)
    
    wQueen = board.pieces(chess.QUEEN, True)
    bQueen = board.pieces(chess.QUEEN, False)
    
    wPawn = board.pieces(chess.PAWN, True)
    bPawn = board.pieces(chess.PAWN, False)
    
    # Calculates the material score
    material_score = (10000 * (len(wKing) - len(bKing)) +
                      3 * (len(wKnight) - len(bKnight)) +
                      3.25 * (len(wBishop) - len(bBishop)) +
                      5 * (len(wRook) - len(bRook)) +
                      9 * (len(wQueen) - len(bQueen)) +
                      1 * (len(wPawn) - len(bPawn))
                    )
    
    white_mobility = 0
    black_mobility = 0
    
    for 

if __name__ == "__main__":
    main()