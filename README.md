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

## Acknowledgements

Special thanks to the kind people who has put up the following resources, without which I wouldn't have been able to complete this:

1. The [Chess Programming Wiki](https://www.chessprogramming.org/Main_Page) for all of the amazing information about creating a chess engine.
2. The [PESTO evaluation function](https://www.chessprogramming.org/PeSTO%27s_Evaluation_Function) which I edited slightly to create the evaluation function used.
3. The [CHess Engine in Python Series](https://www.youtube.com/watch?v=EnYui0e73Rs&list=PLBwF487qi8MGU81nDGaeNE1EnNEPYWKY_) by Eddie Sharick which I took reference from whenever I am stuck or was looking for inspiration.
