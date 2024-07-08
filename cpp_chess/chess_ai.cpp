#include "GameState.h"
#include "chess_logic.h"
#include "generate_moves.h"

bool convert_fen(const std::string_view fen);

using bitboardMapTable = array<array<bitboard, 64>, 2>;

int main(int argc, char *argv[]) {

    init_leapers_attacks();
    GameState game {};

    for (int i = 0; i < 64; ++i) {
        game.print_board(pawn_attacks[black][i]);
    }

    return 0;
}

bool convert_fen(const std::string_view fen) {
    // Takes as input a fen and returns a bitboard

    bitboard board {};
    return true;

}