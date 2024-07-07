#include "GameState.h"
#include "chess_logic.h"
#include "generate_moves.h"

using std::array;

/* Attacks */

/* Defining all of the attack tables */

bitboardMapTable pawn_attacks_map;
const bitboardMapTable& pawn_attacks {pawn_attacks_map};

std::array<bitboard, 64> knight_attacks_map;
const std::array<bitboard, 64> knight_attacks {knight_attacks_map};

/* Attacks using the pawn is generated using a pawn attack table */

constexpr bitboard not_A_file = 18374403900871474942ULL;
constexpr bitboard not_H_file = 9187201950435737471ULL;

// Generates all of the pawn attacks for a pawn at any square specified
bitboard generate_pawn_attacks(int side, int square) {

    // Holds the bitboard of the squares which can be attacked
    bitboard pawn_attacks { 0ULL };
    
    // Placing a bit at the specified square to represent the pawn
    bitboard board { 0ULL };
    set_bit(board, square);

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

// Generates all of the knight attacks for every square where a knight may be at
bitboard generate_knight_attacks(int square) {

    bitboard knight_attacks { 0ULL };

    bitboard board { 0ULL };
    set_bit(board, square);

    // Generate the possible squares that the knight can attack from the square
    knight_attacks |= (board >> 17);

    return knight_attacks;

}
