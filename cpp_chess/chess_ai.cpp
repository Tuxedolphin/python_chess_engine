#include "GameState.h"
#include "chess_logic.h"

bool convert_fen(const std::string_view fen);

int main(int argc, char *argv[]) {

    GameState game_state {};
    game_state.update_board(1, h7);
    game_state.print_board();
    
    cout << '\n';

    game_state.update_board(2, h7);
    game_state.print_board();

    return 0;
}

bool convert_fen(const std::string_view fen) {
    // Takes as input a fen and returns a bitwise map of the board

    uint64_t bitboard {};
    return true;

}