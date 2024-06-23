#include "chess_logic.h"

void print_bitboard(uint64_t bitboard) {
    // Prints a given bitboard

    for (int rank = 0; rank < 8; rank++) {
        for (int file = 0; file < 8; file++) {
            int square = rank * 8 + file;

            std::cout << " " << square << " ";
        }

        std::cout << "\n";
    }
}