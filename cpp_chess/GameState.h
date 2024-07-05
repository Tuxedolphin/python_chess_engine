#ifndef GAMESTATE_H
#define GAMESTATE_H

#include <cstdint>
#include <string_view>

// Holds all the required information about a game state
class GameState {

public:

    GameState(std::string_view) {
        board = 0ULL;
    }

    GameState() = default;

    void update_board(int value, int square);

    void print_board();

    uint64_t get_board() {
        return board;
    }


private:
    uint64_t board { 0ULL };

};

#endif