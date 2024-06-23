#include "chess_logic.h"

int side2move;
int board[64];

int main(int argc, char *argv[]) {

    uint64_t bitboard = 0ULL;
    print_bitboard(bitboard);

    return 0;
}

bool convert_fen(char *fen) {
    // Takes as input a fen and returns a bitwise map of the board

    uint64_t bitboard;
    return true;

}