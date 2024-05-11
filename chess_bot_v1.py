import chess
import chess.polyglot


def main():
    board = chess.Board()
    
    # While the game has not ended
    while 

        # While in opening book
        
            # Get opponent move
            
            # Search for best move and play it
            
        # When out of opening, continue search
    

def opening_search_for_best(board):
    with chess.polyglot.MemoryMappedReader("/Ranomi 1.4.bin") as reader:
        move = get_from_opening(board, reader)
    

def get_from_opening(board, reader: chess.polyglot.MemoryMappedReader):
    """ Returns the most played move according to opening book"""
    return reader.get(board)
        


if __name__ == "__main__":
    main()