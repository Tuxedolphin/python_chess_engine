#include "GameState.h"
#include "chess_logic.h"
#include "generate_moves.h"

using std::array;

/* Attacks */

/* Attacks using the pawn is generated using a pawn attack table */

constexpr bitboard not_A_file = 18374403900871474942ULL;
constexpr bitboard not_H_file = 9187201950435737471ULL;

// Generates all of the pawn attacks in any positions
bitboard generate_pawn_attacks(int side, int square) {

    // Holds the bitboard of the squares which can be attacked
    bitboard pawn_attacks { 0ULL };
    
    // For testing
    GameState game {};
    game.update_board(1, square);

    // Piece bitboard
    bitboard board { game.get_board() };


    if (!side) {
        if ((board >> 7) & not_A_file) pawn_attacks |= (board >> 7);
        if ((board >> 9) & not_H_file) pawn_attacks |= (board >> 9);
    }

    else {
        if ((board << 7) & not_H_file) pawn_attacks |= (board << 7);
        if ((board << 9) & not_A_file) pawn_attacks |= (board << 9);
    }

    return pawn_attacks;

}