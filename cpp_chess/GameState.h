#ifndef GAMESTATE_H
#define GAMESTATE_H

#include <cstdint>
#include <string_view>

using bitboard = uint64_t;

// Holds all the required information about a game state
class GameState {

public:

    // Constructors
    GameState(std::string_view) {
        board = 0ULL;
    }

    GameState() = default;

    void update_board(int value, int square);

    void print_board(bitboard board = 0ULL);

    bitboard get_board() {
        return board;
    }


private:
    // The bitboard which holds the current game state
    bitboard board { 0ULL };

};

#endif