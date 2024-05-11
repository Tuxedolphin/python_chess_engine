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
    
    # Calculates the material score
    material_score = (10000 * (len(board.pieces(chess.KING, True) - len(board.pieces(chess.KING, False)))) +
                      3 * (len(board.pieces(chess.KNIGHT, True) - len(board.pieces(chess.KNIGHT, False)))) +
                      3.25 * (len(board.pieces(chess.BISHOP, True) - len(board.pieces(chess.BISHOP, False)))) +
                      5 * (len(board.pieces(chess.ROOK, True) - len(board.pieces(chess.ROOK, False)))) +
                      9 * (len(board.pieces(chess.QUEEN, True) - len(board.pieces(chess.QUEEN, False)))) +
                      1 * (len(board.pieces(chess.PAWN, True) - len(board.pieces(chess.PAWN, False))))
                    )
    
    white_mobility = 0
    black_mobility = 0
    
    for 

if __name__ == "__main__":
    main()