#include "GameState.h"
#include "chess_logic.h"

// Prints the current bitboard into the terminal as a 2 dimensional array
void GameState::print_board() {
    for (int rank = 0; rank < 8; ++rank) {
        for (int file = 0; file < 8; ++file) {
            int square { rank * 8 + file };

            // Print ranks
            if (!file) cout << "  "s << 8 - rank << "  ";

            cout << get_bit(board, square) << " "s;
        }

        cout << '\n';
    }

    // Print files
    cout << "\n     a b c d e f g h\n";

    // Print the bit
    cout << "     Bitboard: " << board; 
}

// Updates the bitboard
void GameState::update_board(int value, int square) {

    if (value == 2) {
        get_bit(board, square) ? board ^= (1ULL << square) : 0;
    }
    else {
        set_bit(board, square);
    }
}