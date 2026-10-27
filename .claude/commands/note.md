---
description: Add a dated watchlist note for a player
argument-hint: <Name@Team> <note text>
---
Add a watchlist note: $ARGUMENTS

1. Split the arguments into the player (Name@Team) and the note text. If it's unclear, ask.
2. Run `python3 scout.py note "Name@Team" "<note text>"`. Add `--date YYYY-MM-DD` only if the user gave a date.
3. If scout.py reports an ambiguous or unknown player, show the candidates and ask. Never write the file by hand.
4. Confirm in Korean which player (with league) and which file got the note.
