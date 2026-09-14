# Lichess VPS deployment (retired)

How this engine ran as a Lichess BOT through
[lichess-bot](https://github.com/lichess-bot-devs/lichess-bot) in Docker on the VPS, until
September 2026, when TuxedolphinBot (`Tuxedolphin/tuxedolphin-chess-bot`) replaced it on the
same machine.

| File | Role |
|---|---|
| `Dockerfile`, `compose.yaml` | lichess-bot image and service definition |
| `config.yml.example` | lichess-bot settings; copy to `config.yml` and add the bot token |
| `engine/uci.py`, `engine/opening_book.py` | the deployed variants of the repository's `uci.py` and `opening_book.py` |

Every other file the deployment used (`python_chess/`, `scripts/`) is identical to this
repository's copy and is not duplicated here.
