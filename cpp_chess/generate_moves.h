#ifndef GENERATE_MOVES_H
#define GENERATE_MOVES_H

#include "chess_logic.h"

/* Defining all of the attack tables */

extern bitboardMapTable pawn_attacks_map;
extern const bitboardMapTable& pawn_attacks {pawn_attacks_map};

extern std::array<bitboard, 64> knight_attacks_map;
extern const std::array<bitboard, 64> knight_attacks {knight_attacks_map};

bitboard generate_pawn_attacks(int side, int square);
bitboard generate_knight_attacks(int square);

#endif