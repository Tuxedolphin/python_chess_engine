FROM lichessbotdevs/lichess-bot:latest

RUN apt-get update && \
    apt-get install -y --no-install-recommends pypy3 && \
    rm -rf /var/lib/apt/lists/*
