#ifndef CHESS_LOGIC_H
#define CHESS_LOGIC_H

#include <cstdint>
#include <iostream>
#include <string>
#include <string_view>
#include <array>

using namespace std::literals;
using std::array;
using std::cout;

using bitboard = uint64_t;
using bitboardMapTable = array<array<bitboard, 64>, 2>;

// Define inline functions for accessing bits

// Getting the bit at the square location
inline int get_bit(const bitboard &board, int square) {
    return (board & (1ULL << square) ? 1 : 0);
}

// Setting the bit at the square to be 1
inline void set_bit(bitboard &board, int square) {
    board |= (1ULL << square);
}

// Setting the bit at the square to be 0 
inline void remove_bit(bitboard &board, int square) {
    ((1ULL << square) ? 1 : 0) ? board ^= (1ULL, square) : 0;
}

// Define board squares
enum Squares {
    a8, b8, c8, d8, e8, f8, g8, h8,
    a7, b7, c7, d7, e7, f7, g7, h7,
    a6, b6, c6, d6, e6, f6, g6, h6,
    a5, b5, c5, d5, e5, f5, g5, h5,
    a4, b4, c4, d4, e4, f4, g4, h4,
    a3, b3, c3, d3, e3, f3, g3, h3,
    a2, b2, c2, d2, e2, f2, g2, h2,
    a1, b1, c1, d1, e1, f1, g1, h1,
};

// Define the type of pieces
enum class Pieces {
    empty,
    pawn,
    bishop,
    knight,
    rook,
    queen,
    king,
};

enum SideToMove {
    white, black,
};

#endif