# CLI Usage Guide - Music Playlist Application

## Quick Start

### Interactive Mode
```bash
python main.py
```

### Demo Mode
```bash
python main.py --demo
```

### Running Tests
```bash
pytest tests/test_cli.py -v
```

---

## Command Reference

### ADD - Add a Track to Library
```
ADD <titulo> <artista> <genero> <bpm>
```

**Parameters:**
- `titulo`: Track title (string, required)
- `artista`: Artist name (string, required)
- `genero`: Genre/category (string, required)
- `bpm`: Beats per minute (positive integer, required)

**Example:**
```
ADD "Midnight City" "M83" "Synthwave" 95
```

**Notes:**
- All parameters with spaces must be enclosed in quotes
- BPM must be a positive integer
- This automatically rebuilds mood queues

---

### REMOVE - Remove a Track
```
REMOVE <id>
```

**Parameters:**
- `id`: Track ID (integer, required)

**Example:**
```
REMOVE 5
```

**Notes:**
- IDs are assigned sequentially and are never reused
- This automatically rebuilds mood queues

---

### SEARCH - Search for a Track
```
SEARCH <titulo|id>
```

**Parameters:**
- `titulo|id`: Either a track title or ID

**Examples:**
```
SEARCH "My Song"     # Search by title
SEARCH 3             # Search by ID
```

**Notes:**
- Title search is case-insensitive
- Returns the first exact match by title
- By ID always returns the unique track

---

### LIST - Display All Tracks
```
LIST
```

**Example:**
```
LIST
```

**Output:**
```
✓ Library:
[1] Midnight City - M83 (95 BPM, Synthwave)
[2] Run - AWOLNATION (128 BPM, Electronic)
```

---

### REBUILD - Rebuild Mood Queues
```
REBUILD
```

**Example:**
```
REBUILD
```

**Notes:**
- Clears all mood queues and redistributes tracks by BPM
- Automatically called when adding or removing tracks
- Useful for manual batch updates

---

### QUEUE - Display a Mood Queue
```
QUEUE <mood>
```

**Parameters:**
- `mood`: One of: Relaxar, Focar, Animar, Treinar

**Examples:**
```
QUEUE Relaxar       # Show relaxation playlist
QUEUE Focar         # Show focus playlist
```

**Mood Classifications (by BPM):**
- **Relaxar**: BPM ≤ 80 (gentle, wind-down music)
- **Focar**: 81 ≤ BPM ≤ 120 (work, study, concentration)
- **Animar**: 121 ≤ BPM ≤ 160 (upbeat, activity music)
- **Treinar**: BPM > 160 (high-intensity, workout music)

---

### PLAY - Play Next Track
```
PLAY
```

**Example:**
```
PLAY
```

**Output:**
```
✓ Now playing: Midnight City by M83 (from Focar)
```

**Notes:**
- Plays the next track from priority queue order: Focar → Relaxar → Animar → Treinar
- Removes track from queue (dequeue operation)
- Adds track to playback history
- Returns error if no tracks available

---

### HISTORY - Show Playback History
```
HISTORY
```

**Example:**
```
HISTORY
```

**Output:**
```
✓ Playback history (3 tracks):
1. Midnight City - M83
2. Run - AWOLNATION
3. Song Name - Artist Name
```

**Notes:**
- Shows all played tracks in order
- Does not modify history (read-only)
- FIFO queue: first played appears first

---

### STATS - Show Statistics
```
STATS
```

**Example:**
```
STATS
```

**Output:**
```
✓ Library: 5 tracks
Relaxar: 1
Focar: 2
Animar: 1
Treinar: 1
History: 3 plays
```

**Notes:**
- Shows total tracks in library
- Shows distribution across mood queues
- Shows total plays in history
- Useful for monitoring collection

---

### HELP - Show Available Commands
```
HELP
```

**Example:**
```
HELP
```

**Notes:**
- Displays full command reference in CLI
- Same information as this guide

---

### EXIT - Terminate Session
```
EXIT
```

**Example:**
```
EXIT
```

**Notes:**
- Gracefully closes the CLI
- Ctrl+C also works in interactive mode

---

## Mood Queue Behavior

### How Tracks Are Classified

Tracks are automatically classified into mood queues based on their BPM:

```
BPM <= 80            →  Relaxar
81 <= BPM <= 120     →  Focar
121 <= BPM <= 160    →  Animar
BPM > 160            →  Treinar
```

### When Classification Happens

- **On ADD**: New track immediately classified and added to queues
- **On REMOVE**: Track removed from all queues, other queues rebuilt
- **On REBUILD**: All queues cleared and regenerated from library

---

## Batch Mode - Execute Commands from File

Commands can be executed from a file (one per line):

```python
from cli import run_batch
from app import SistemaPlaylist

sistema = SistemaPlaylist()
run_batch(sistema, "commands.cli")
```

### Example Batch File (commands.cli):

```
# Comments start with # and are ignored

# Add tracks
ADD "Song 1" "Artist 1" "Genre 1" 80
ADD "Song 2" "Artist 2" "Genre 2" 120
ADD "Song 3" "Artist 3" "Genre 3" 150

# Show library
LIST

# Rebuild queues
REBUILD

# Show mood queues
QUEUE Relaxar
QUEUE Focar
QUEUE Animar

# Play some tracks
PLAY
PLAY

# Show history
HISTORY

# Show statistics
STATS
```

---

## Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| `Unknown command: X` | Command not recognized | Check command spelling (case-insensitive) |
| `X requires N parameter(s)` | Missing required parameters | Add all required parameters |
| `Unmatched quotes` | Quote mismatch in parameters | Ensure all quotes are properly closed |
| `BPM must be a positive integer` | Invalid BPM value | Use a number > 0 for BPM |
| `Invalid mood` | Invalid mood name | Use: Relaxar, Focar, Animar, or Treinar |
| `Track not found` | Searched track doesn't exist | Verify ID or exact title match |
| `No tracks available to play` | Empty queues | Add tracks first |

---

## Interactive Session Example

```
🎵 Playlist CLI - Type 'HELP' for commands or 'EXIT' to quit

> ADD "Midnight City" "M83" "Synthwave" 95
✓ Track added: Midnight City (ID: 1, 95 BPM)

> ADD "Run" "AWOLNATION" "Electronic" 128
✓ Track added: Run (ID: 2, 128 BPM)

> LIST
✓ Library:
[1] Midnight City - M83 (95 BPM, Synthwave)
[2] Run - AWOLNATION (128 BPM, Electronic)

> REBUILD
✓ Queues rebuilt: Relaxar=0, Focar=1, Animar=1, Treinar=0

> QUEUE Focar
✓ Queue 'Focar' (1 tracks):
[1] Midnight City - M83 (95 BPM, Synthwave)

> PLAY
✓ Now playing: Midnight City by M83 (from Focar)

> HISTORY
✓ Playback history (1 tracks):
1. Midnight City - M83

> STATS
✓ Library: 2 tracks
Relaxar: 0
Focar: 0
Animar: 1
Treinar: 0
History: 1 plays

> EXIT
✓ Goodbye!
```

---

## Advanced Usage

### Using CLI from Python Code

```python
from app import SistemaPlaylist
from cli import CommandParser, CommandExecutor

# Create system and executor
sistema = SistemaPlaylist()
executor = CommandExecutor(sistema)
parser = CommandParser()

# Parse and execute a command
cmd, params = parser.parse_line('ADD "Song" "Artist" "Pop" 120')
result = executor.execute(cmd, params)
print(result)
```

### Handling Errors Programmatically

```python
from cli import ParseError, ValidationError

try:
    cmd, params = parser.parse_line(user_input)
    result = executor.execute(cmd, params)
except ParseError as e:
    print(f"Parse error: {e}")
except ValidationError as e:
    print(f"Validation error: {e}")
```

---

## Tips and Best Practices

1. **Always REBUILD after bulk modifications** to ensure queues are in sync
2. **Use quotes for parameters with spaces** - e.g., `ADD "My Song" "My Artist" "My Genre" 100`
3. **Search by ID for fast lookups** - `SEARCH 5` is faster than title search
4. **Check STATS regularly** to monitor library distribution
5. **Use batch files for testing** - put commands in .cli file and use `run_batch()`
6. **Remember mood boundaries** - 80, 120, 160 are the BPM thresholds

---

## File Structure

```
/workspaces/fatec-ed-playlist/
├── app.py              # Core domain: Musica, Biblioteca, Fila, SistemaPlaylist
├── cli.py              # CLI implementation: LineReader, Parser, Executor, REPL
├── main.py             # Entry point (uses CLI)
├── commands.cli        # Example batch commands file
├── tests/
│   └── test_cli.py    # Unit tests for CLI module
└── docs/
    ├── CLI.md         # Detailed CLI architecture (this replaces it)
    ├── PLAN.md        # Original requirements
    ├── BACKEND.md     # Backend architecture plan
    └── FRONTEND.md    # Frontend architecture plan
```

---

## Troubleshooting

### "No module named 'cli'"
- Make sure you're running from `/workspaces/fatec-ed-playlist/` directory
- Verify cli.py exists in the project root

### "No input provided" or frozen terminal
- Press Ctrl+C to interrupt
- Type a command and press Enter to continue

### Batch file not running
- Verify file path is correct
- Check file ends with newline
- Ensure comments use `#` before each line

### BPM out of range
- BPM must be > 0
- Max practical BPM is around 300 (for extreme music)

---

## Support

For more information:
- See `/workspaces/fatec-ed-playlist/docs/CLI.md` for architecture details
- See `/workspaces/fatec-ed-playlist/docs/PLAN.md` for requirements
- Type `HELP` in the CLI for command reference
- Run tests: `pytest tests/test_cli.py -v`
