#include "GameState.h"
#include "chess_logic.h"
#include "generate_moves.h"

using std::array;

/* Attacks */

/* Defining all of the attack tables */

std::array<bitboardMapTable, 2> pawn_attacks_map {};
const std::array<bitboardMapTable, 2>& pawn_attacks {pawn_attacks_map};

bitboardMapTable knight_attacks_map {};
const bitboardMapTable& knight_attacks {knight_attacks_map};

bitboardMapTable king_attacks_map {};
const bitboardMapTable& king_attacks {king_attacks_map};

/* Attacks using the pawn is generated using a pawn attack table */

constexpr bitboard not_A_file { 18374403900871474942ULL };
constexpr bitboard not_H_file { 9187201950435737471ULL };

// Generates all of the pawn attacks for a pawn at any square specified
bitboard generate_pawn_attacks(const int side, const int square) {

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

/* Attacks using the knight is generated using a knight attack table */

constexpr bitboard not_HG_file { 4557430888798830399ULL };
constexpr bitboard not_AB_file { 18229723555195321596ULL };

// Generates all of the knight attacks for every square where a knight may be at
bitboard generate_knight_attacks(int square) {

    bitboard knight_attacks { 0ULL };

    bitboard board { 0ULL };
    set_bit(board, square);

    // Generate the possible squares that the knight can attack from the square
    if ((board >> 17) & not_H_file) knight_attacks |= (board >> 17);
    if ((board >> 15) & not_A_file) knight_attacks |= (board >> 15);
    if ((board >> 10) & not_HG_file) knight_attacks |= (board >> 10);
    if ((board >> 6) & not_AB_file) knight_attacks |= (board >> 6);

    if ((board << 17) & not_A_file) knight_attacks |= (board << 17);
    if ((board << 15) & not_H_file) knight_attacks |= (board << 15);
    if ((board << 10) & not_AB_file) knight_attacks |= (board << 10);
    if ((board << 6) & not_HG_file) knight_attacks |= (board << 6);

    return knight_attacks;

}

/* Attacks for the king is generated using a king attack table */

// Generates all the king attacks for every square where the king may be at
bitboard generate_king_attacks(int square) {

    bitboard king_attacks { 0ULL };

    bitboard board { 0ULL };
    set_bit(board, square);

    if ((board >> 9) & not_H_file) king_attacks |= (board >> 9);
    if (board >> 8) king_attacks |= (board >> 8);
    if ((board >> 7) & not_A_file) king_attacks |= (board >> 7);
    if ((board >> 1) & not_H_file) king_attacks |= (board >> 1);

    if ((board << 9) & not_A_file) king_attacks |= (board << 9);
    if (board << 8) king_attacks |= (board << 8);
    if ((board << 7) & not_H_file) king_attacks |= (board << 7);
    if ((board << 1) & not_A_file) king_attacks |= (board << 1);



    return king_attacks;

}

// Generates all of the attacks
constexpr void init_leapers_attacks() {

    for (int square = 0; square < 64; ++square) {
        // Initialises the pawn attacks
        pawn_attacks_map[white][square] = generate_pawn_attacks(white, square);
        pawn_attacks_map[black][square] = generate_pawn_attacks(black, square);

        // Initialises the knight attacks
        knight_attacks_map[square] = generate_knight_attacks(square);
        knight_attacks_map[square] = generate_knight_attacks(square);

        // Initialises the king attacks
        king_attacks_map[square] = generate_king_attacks(square);
        king_attacks_map[square] = generate_king_attacks(square);
    
    }
}

// For testing to make sure the functions are working
int main() {
    GameState game {};

    // game.print_board(generate_king_attacks(h4));

    init_leapers_attacks();

    for (int square = 0; square < 64; ++square) {
        game.print_board(king_attacks[square]);
    }
}