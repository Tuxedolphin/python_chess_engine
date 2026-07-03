# Python Chess Engine

This is a simple python chess engine with all the essentials - moving generation, move searching, nega-max algorithm - and some more advanced features such as piece table evaluation function and move ordering. A UI is also included which includes move highlighting and a UI for choosing which colour(s) the AI plays.

## Getting Started

### Prerequisites

As this project is entirely built in python3, please make sure that you have Python 3 installed on your device. You can download it from [the following link](https://www.python.org/downloads/) if you have not done so.

### Installation

To install the engine, download the file directly from Git Hub or create a fork of the repository using the forked repository.

After installing the folder, open the terminal and change the directory to this file. Then, run the following to install all the extensions used:

```
pip install -r requirements.txt
```

Thereafter, simply run the file `chess_game.py`, either from the terminal or using a code editor. A main menu should pop up as shown below:

<div align="center">
  <img width="570" alt="chess_engine_menu" src="https://github.com/user-attachments/assets/f999abb0-fb5c-40e6-81f0-59cac7a05558">
</div>

## Navigating The UI

By default, you will be playing the white pieces and the engine will be playing black. To change this, simply click on options, which will bring up the options menu:

<div align="center">
  <img width="572" alt="chess_engine_options" src="https://github.com/user-attachments/assets/5671bdc8-3151-4f58-80b0-54a4752b7fbd">
</div>

Simply click on the options that you desire. The options selected is automatically saved and you can simply exit back to the main menu.

> [!IMPORTANT]
> This program supports human vs human and ai vs ai. However, do note that if you choose ai vs ai, it is not possible to stop the program other than terminating it or waiting till the game is over.

After clicking on "play", a similar screen to this will greet you (of course, this screenshot has been played out to demonstrate the UI).
<div align="center">
  <img width="571" alt="chess_engine_play" src="https://github.com/user-attachments/assets/4605d045-16f2-446d-bbaf-3bf9c6cb901a">
</div>

Note the following:

1. The piece marked yellow is the last move made.
2. The piece marked blue is the current piece selected.
3. The squares marked red are the squares that the selected piece can move to.
4. The pgn of the game is avaliable on the right hand side.
5. To undo a move, press the `left arrow` key. To restart the game, press the `PgDn` key.

When the game is over, a screen similar to this will show:

<div align="center">
  <img width="569" alt="chess_engine_over" src="https://github.com/user-attachments/assets/22c37e0e-f80c-475f-876d-f22119721a63">
</div>

> [!IMPORTANT]
> Do not undo a move if it was a move made by the AI. As this engine is largely deterministic in nature as the evaluation function usually leads to only 1 best move, undoing a move will only make the engine think again and play the same move. Spamming the button will not work either but will only cause a backlog of undo moves, creating more lag.

> [!NOTE]
> Note that the number of positions searched by the AI as well as the evaluation of the move played is printed in the terminal. Do note that the evaluation is always positive for the AI, i.e. no matter the colour, the higher the number, the better the AI thinks the move is. If the AI sees mate, the evaluation will either be 100000 (if it is mating) or -100000 (if it is getting mated). To translate the evaluation to our what we commonly use, simply divide the number by 100.

## UCI Support

The engine speaks [UCI](https://www.chessprogramming.org/UCI) via `uci.py` (requires Python 3.10+), so it can be loaded into any standard chess GUI (Arena, Cute Chess, BanksiaGUI) or match runner:

```
python3 uci.py
```

`scripts/engine.sh` is a launcher that picks a suitable Python and starts the adapter — point GUIs and tools at that. Search depth defaults to 3 and can be changed with `setoption name Depth value N` or `go depth N`.

## Estimating Its Strength

`scripts/estimate_elo.sh` plays rating matches against strength-limited [Stockfish](https://stockfishchess.org/) using [fastchess](https://github.com/Disservin/fastchess) and prints an Elo estimate per level:

```
brew install stockfish
ROUNDS=15 LEVELS="1320 1400 1500" scripts/estimate_elo.sh
```

Games and logs land in `elo_results/`. Note that Stockfish's `UCI_Elo` floor is 1320, so if the engine scores near zero at every level, the more meaningful number is its online rating from real games (below).

## Playing It Online

The engine runs on Lichess through [lichess-bot](https://github.com/lichess-bot-devs/lichess-bot), which both lets anyone challenge it and gives it a real Lichess rating from rated games:

1. Clone lichess-bot and install its requirements (Python 3.10+ venv recommended).
2. Create a new Lichess account for the bot (it must have played no games), generate a personal API token with the `bot:play` scope, and put it in lichess-bot's `config.yml`.
3. In `config.yml`, set `engine.dir` to this repository's `scripts/` folder, `engine.name` to `engine.sh`, `engine.working_dir` to this repository's root, and `go_commands: depth: 3`.
4. Upgrade the account to a bot account and start it:

```
python3 lichess-bot.py -u
```

Once online, anyone can play it at `https://lichess.org/@/<bot-username>`.

## Acknowledgements

Special thanks to the kind people who has put up the following resources, without which I wouldn't have been able to complete this:

1. The [Chess Programming Wiki](https://www.chessprogramming.org/Main_Page) for all of the amazing information about creating a chess engine.
2. The [PESTO evaluation function](https://www.chessprogramming.org/PeSTO%27s_Evaluation_Function) which I edited slightly to create the evaluation function used.
3. The [Chess Engine in Python Series](https://www.youtube.com/watch?v=EnYui0e73Rs&list=PLBwF487qi8MGU81nDGaeNE1EnNEPYWKY_) by Eddie Sharick which I took reference from whenever I am stuck or was looking for inspiration.
