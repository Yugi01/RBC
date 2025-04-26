#!/bin/bash

mkdir -p prev_games
export PYTHONPATH=.
rc-play trout_bot

# Find the most recent JSON file (whatever it's called)
LATEST_JSON=$(ls -t *.json | head -n 1)

if [ -n "$LATEST_JSON" ]; then
  mv "$LATEST_JSON" "prev_games/$LATEST_JSON"
  echo "✅ Saved game moved to prev_games/$LATEST_JSON"
else
  echo "⚠️ No saved game found!"
fi
