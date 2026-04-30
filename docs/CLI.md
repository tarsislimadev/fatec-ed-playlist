# CLI - Line-by-Line Input Application Plan

## Overview

The CLI (Command Line Interface) module provides a **line-by-line input stream processor** for the music playlist system. This document outlines the architecture, input handling strategy, and integration patterns for building a Python application that reads commands sequentially from stdin and executes them against the `SistemaPlaylist` domain.

---

## 1. Architecture

### 1.1 Core Components

```
┌─────────────────────────────────────────┐
│         Input Stream (stdin)            │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│    LineReader (async/blocking)          │
│  • read_line()                          │
│  • parse_line()                         │
│  • validate_syntax()                    │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│    CommandParser (state machine)        │
│  • tokenize (split by delimiters)       │
│  • map to MenuOption enum               │
│  • validate parameters                  │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│    CommandExecutor (domain orchestration)
│  • dispatch to SistemaPlaylist methods  │
│  • handle exceptions                    │
│  • format output                        │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│       Output Formatter (stdout/stderr)  │
│  • serialize results                    │
│  • print formatted text                 │
│  • render tables/lists                  │
└─────────────────────────────────────────┘
```

### 1.2 Input/Output Protocol

**Input Format** (one command per line):
```
<COMMAND> [PARAM1] [PARAM2] ... [PARAMn]
```

**Output Format**:
```
✓ <SUCCESS_MESSAGE>
✗ <ERROR_MESSAGE>
```

---

## 2. Line Reader Module

### 2.1 Blocking Mode (Standard)

Reads lines sequentially from stdin until EOF or termination signal.

```python
class LineReader:
    """Reads and buffers input lines from stdin."""
    
    def __init__(self, buffer_size: int = 1024):
        self.buffer_size = buffer_size
        self.line_count = 0
    
    def read_line(self) -> Optional[str]:
        """
        Read a single line from stdin, strip whitespace.
        
        Returns:
            str: Line content (empty if blank)
            None: EOF reached
        """
        try:
            line = input()  # Blocks until user presses Enter
            self.line_count += 1
            return line.strip()
        except EOFError:
            return None  # EOF or Ctrl+D
        except KeyboardInterrupt:
            raise  # Ctrl+C - propagate
    
    def read_lines(self) -> Iterator[str]:
        """
        Generator that yields lines until EOF.
        
        Yields:
            str: Each non-empty line
        """
        while True:
            line = self.read_line()
            if line is None:
                break
            if line:  # Skip empty lines
                yield line
```

### 2.2 Async Mode (Optional - for future)

For integration with async frameworks (FastAPI background tasks, asyncio):

```python
import asyncio

class AsyncLineReader:
    """Async line reader for non-blocking I/O."""
    
    async def read_line_async(self) -> Optional[str]:
        """Read one line asynchronously."""
        loop = asyncio.get_event_loop()
        # Delegate to thread pool to avoid blocking
        return await loop.run_in_executor(None, input)
    
    async def read_lines_async(self) -> AsyncIterator[str]:
        """Generator yielding lines asynchronously."""
        while True:
            line = await self.read_line_async()
            if line is None:
                break
            if line.strip():
                yield line.strip()
```

---

## 3. Command Parser

### 3.1 Syntax Definition

**Menu Command Mapping**:

| Command | Params | Description |
|---------|--------|-------------|
| `ADD` | titulo artista genero bpm | Add track to library |
| `REMOVE` | id | Remove track from library |
| `SEARCH` | titulo \| id | Search track by title or ID |
| `LIST` | - | List all tracks |
| `REBUILD` | - | Rebuild mood queues |
| `QUEUE` | mood_name | Show tracks in mood queue (Relaxar\|Focar\|Animar\|Treinar) |
| `PLAY` | - | Play next track (dequeue + history) |
| `HISTORY` | - | Show playback history |
| `STATS` | - | Show system statistics |
| `EXIT` | - | Terminate CLI |

### 3.2 Parser Implementation

```python
from enum import Enum
from typing import Dict, List, Tuple

class MenuOption(Enum):
    ADD = "ADD"
    REMOVE = "REMOVE"
    SEARCH = "SEARCH"
    LIST = "LIST"
    REBUILD = "REBUILD"
    QUEUE = "QUEUE"
    PLAY = "PLAY"
    HISTORY = "HISTORY"
    STATS = "STATS"
    EXIT = "EXIT"

class CommandParser:
    """Parses raw input lines into (command, params) tuples."""
    
    COMMAND_MAP = {opt.value: opt for opt in MenuOption}
    
    @staticmethod
    def parse_line(line: str) -> Tuple[MenuOption, List[str]]:
        """
        Parse a line into (MenuOption, list[params]).
        
        Args:
            line: Raw input string
        
        Returns:
            Tuple of (MenuOption, [param1, param2, ...])
        
        Raises:
            ValueError: If command invalid or params missing
        """
        tokens = line.split()
        if not tokens:
            raise ValueError("Empty command")
        
        command_str = tokens[0].upper()
        if command_str not in CommandParser.COMMAND_MAP:
            raise ValueError(f"Unknown command: {command_str}")
        
        menu_opt = CommandParser.COMMAND_MAP[command_str]
        params = tokens[1:]
        
        # Validate param count
        required_params = CommandParser._get_param_count(menu_opt)
        if len(params) < required_params:
            raise ValueError(
                f"{command_str} requires {required_params} "
                f"parameter(s), got {len(params)}"
            )
        
        return menu_opt, params
    
    @staticmethod
    def _get_param_count(opt: MenuOption) -> int:
        """Return minimum required params for command."""
        rules = {
            MenuOption.ADD: 4,      # titulo artista genero bpm
            MenuOption.REMOVE: 1,   # id
            MenuOption.SEARCH: 1,   # titulo or id
            MenuOption.LIST: 0,
            MenuOption.REBUILD: 0,
            MenuOption.QUEUE: 1,    # mood_name
            MenuOption.PLAY: 0,
            MenuOption.HISTORY: 0,
            MenuOption.STATS: 0,
            MenuOption.EXIT: 0,
        }
        return rules.get(opt, 999)  # Default: require all
```

---

## 4. Command Executor

### 4.1 Orchestration Pattern

```python
from typing import Callable, Dict

class CommandExecutor:
    """
    Dispatches parsed commands to SistemaPlaylist methods.
    Maps MenuOption → handler function.
    """
    
    def __init__(self, sistema: 'SistemaPlaylist'):
        self.sistema = sistema
        self.handlers: Dict[MenuOption, Callable] = {
            MenuOption.ADD: self._handle_add,
            MenuOption.REMOVE: self._handle_remove,
            MenuOption.SEARCH: self._handle_search,
            MenuOption.LIST: self._handle_list,
            MenuOption.REBUILD: self._handle_rebuild,
            MenuOption.QUEUE: self._handle_queue,
            MenuOption.PLAY: self._handle_play,
            MenuOption.HISTORY: self._handle_history,
            MenuOption.STATS: self._handle_stats,
            MenuOption.EXIT: self._handle_exit,
        }
    
    def execute(self, cmd: MenuOption, params: List[str]) -> str:
        """
        Execute a command and return formatted output.
        
        Args:
            cmd: MenuOption enum
            params: List of parameter strings
        
        Returns:
            str: Formatted output (success/error message)
        """
        try:
            if cmd not in self.handlers:
                return f"✗ Unknown command: {cmd}"
            
            handler = self.handlers[cmd]
            result = handler(*params)
            return self._format_success(result)
        
        except ValueError as e:
            return f"✗ Invalid params: {str(e)}"
        except Exception as e:
            return f"✗ Error: {str(e)}"
    
    # Handler methods (examples)
    
    def _handle_add(self, titulo: str, artista: str, genero: str, bpm: str) -> str:
        """ADD titulo artista genero bpm"""
        try:
            bpm_int = int(bpm)
            if bpm_int <= 0:
                raise ValueError("BPM must be > 0")
            self.sistema.adicionar_musica(titulo, artista, genero, bpm_int)
            return f"Track added: {titulo} ({bpm_int} BPM)"
        except ValueError:
            raise ValueError("BPM must be a positive integer")
    
    def _handle_remove(self, track_id: str) -> str:
        """REMOVE id"""
        try:
            track_id_int = int(track_id)
            if not self.sistema.remover_musica(track_id_int):
                return "✗ Track not found"
            return f"Track {track_id_int} removed"
        except ValueError:
            raise ValueError("ID must be an integer")
    
    def _handle_search(self, query: str) -> str:
        """SEARCH titulo|id"""
        # Try ID first
        try:
            track_id = int(query)
            track = self.sistema.pesquisar_musica_por_id(track_id)
            if track:
                return self._format_track(track)
            return "✗ Track not found by ID"
        except ValueError:
            pass
        
        # Try title
        track = self.sistema.pesquisar_musica_por_titulo(query)
        if track:
            return self._format_track(track)
        return "✗ Track not found by title"
    
    def _handle_list(self) -> str:
        """LIST"""
        tracks = list(self.sistema.listar_musicas())
        if not tracks:
            return "Library is empty"
        return "\n".join(self._format_track(t) for t in tracks)
    
    def _handle_stats(self) -> str:
        """STATS"""
        stats = self.sistema.obter_estatisticas()
        return (
            f"Library: {stats['total_tracks']} tracks\n"
            f"Relaxar: {stats['relaxar']}\n"
            f"Focar: {stats['focar']}\n"
            f"Animar: {stats['animar']}\n"
            f"Treinar: {stats['treinar']}"
        )
    
    def _handle_exit(self) -> str:
        """EXIT"""
        raise SystemExit("Exiting CLI")
    
    def _format_track(self, track: 'Musica') -> str:
        """Format track for display."""
        return f"[{track.id}] {track.titulo} - {track.artista} ({track.bpm} BPM, {track.genero})"
    
    def _format_success(self, msg: str) -> str:
        """Wrap success message with ✓ indicator."""
        return f"✓ {msg}" if msg and not msg.startswith("✗") else msg
```

---

## 5. Main CLI Loop

### 5.1 REPL Pattern (Interactive)

```python
import sys

class REPL:
    """
    Read-Eval-Print Loop: continuously reads commands,
    executes them, and prints results.
    """
    
    def __init__(self, sistema: 'SistemaPlaylist'):
        self.reader = LineReader()
        self.parser = CommandParser()
        self.executor = CommandExecutor(sistema)
        self.running = True
    
    def run(self):
        """Main REPL loop."""
        print("🎵 Playlist CLI - Type 'HELP' for commands or 'EXIT' to quit")
        
        for line in self.reader.read_lines():
            try:
                cmd, params = self.parser.parse_line(line)
                
                if cmd == MenuOption.EXIT:
                    print("✓ Goodbye!")
                    break
                
                output = self.executor.execute(cmd, params)
                print(output)
            
            except ValueError as e:
                print(f"✗ Parse error: {str(e)}")
            except KeyboardInterrupt:
                print("\n✗ Interrupted")
                break
            except Exception as e:
                print(f"✗ Unexpected error: {str(e)}")
                sys.exit(1)
```

### 5.2 Batch Mode (Scripted)

```python
def run_batch(sistema: 'SistemaPlaylist', filepath: str):
    """
    Execute commands from a file (one per line).
    Useful for testing and automation.
    """
    parser = CommandParser()
    executor = CommandExecutor(sistema)
    
    try:
        with open(filepath, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith('#'):  # Skip comments
                    continue
                
                try:
                    cmd, params = parser.parse_line(line)
                    if cmd == MenuOption.EXIT:
                        break
                    output = executor.execute(cmd, params)
                    print(f"[Line {line_num}] {output}")
                except Exception as e:
                    print(f"[Line {line_num}] ✗ Error: {str(e)}")
    
    except FileNotFoundError:
        print(f"✗ File not found: {filepath}")
```

---

## 6. Error Handling Strategy

### 6.1 Exception Hierarchy

```
CLIException (base)
├── ParseError        # Input syntax invalid
├── ValidationError   # Params invalid (e.g., BPM <= 0)
├── StateError        # Domain state invalid (e.g., empty queue)
└── RuntimeError      # Unexpected failure
```

### 6.2 Handling Patterns

```python
class CLIException(Exception):
    """Base exception for CLI errors."""
    pass

class ParseError(CLIException):
    """Raised when input cannot be parsed."""
    pass

class ValidationError(CLIException):
    """Raised when params fail validation."""
    pass

def safe_execute(cmd: MenuOption, params: List[str]) -> str:
    """Execute with comprehensive error handling."""
    try:
        # Domain logic
        return executor.execute(cmd, params)
    
    except ValidationError as e:
        return f"✗ Validation failed: {str(e)}"
    except StateError as e:
        return f"✗ Invalid state: {str(e)}"
    except ParseError as e:
        return f"✗ Parse error: {str(e)}"
    except Exception as e:
        # Log unexpected errors for debugging
        import traceback
        traceback.print_exc()
        return f"✗ Internal error (see logs)"
```

---

## 7. Input Validation Rules

### 7.1 Per-Command Validation

| Command | Rule | Example |
|---------|------|---------|
| `ADD` | BPM must be int > 0; titulo/artista/genero non-empty | `ADD "Song Name" "Artist" "Pop" 120` |
| `REMOVE` | ID must exist in library | `REMOVE 5` |
| `SEARCH` | Query non-empty; must match titulo or id | `SEARCH "Song"` or `SEARCH 3` |
| `QUEUE` | mood_name in {Relaxar, Focar, Animar, Treinar} | `QUEUE Relaxar` |

### 7.2 Global Sanitization

```python
def sanitize_input(line: str) -> str:
    """
    Sanitize raw input:
    - Remove leading/trailing whitespace
    - Collapse internal whitespace (except in quoted strings)
    - Remove control characters
    """
    line = line.strip()
    
    # Basic control char removal
    line = ''.join(c for c in line if ord(c) >= 32 or c in '\t\n')
    
    return line

def parse_quoted_params(line: str) -> List[str]:
    """
    Parse params respecting quoted strings.
    
    Example:
        input:  ADD "My Song" Artist Pop 120
        output: ['ADD', 'My Song', 'Artist', 'Pop', '120']
    """
    import shlex
    try:
        return shlex.split(line)
    except ValueError as e:
        raise ParseError(f"Unmatched quotes: {str(e)}")
```

---

## 8. Integration with app.py

### 8.1 Current app.py Structure

The original `app.py` contains:
- `SistemaPlaylist` class with methods: `adicionar_musica()`, `remover_musica()`, `listar_musicas()`, etc.
- Existing `executar_menu()` function (interactive menu loop)
- `executar_demo()` function (pre-populated demo mode)

### 8.2 Refactoring Strategy

**Option A: Adapt existing app.py to use CLI.md architecture**
```python
# In app.py - replace executar_menu() with:

from cli import REPL

def main():
    sistema = SistemaPlaylist()
    
    if '--demo' in sys.argv:
        executar_demo(sistema)
    else:
        repl = REPL(sistema)
        repl.run()

if __name__ == '__main__':
    main()
```

**Option B: Create separate cli.py module**
```
app.py       (keeps original domain: Musica, Biblioteca, Fila, SistemaPlaylist)
cli.py       (new module: LineReader, CommandParser, CommandExecutor, REPL)
main.py      (entry point: orchestrates system + CLI)
```

---

## 9. Example Session

```
🎵 Playlist CLI - Type 'HELP' for commands or 'EXIT' to quit

> ADD "Midnight City" "M83" "Synthwave" 95
✓ Track added: Midnight City (95 BPM)

> ADD "Run" "Awolnation" "Electronic" 128
✓ Track added: Run (128 BPM)

> LIST
✓ [1] Midnight City - M83 (95 BPM, Synthwave)
✓ [2] Run - Awolnation (128 BPM, Electronic)

> REBUILD
✓ Queues rebuilt: Relaxar=0, Focar=2, Animar=0, Treinar=0

> QUEUE Focar
✓ [1] Midnight City (95 BPM)
✓ [2] Run (128 BPM)

> PLAY
✓ Now playing: Midnight City by M83
✓ Added to history

> HISTORY
✓ 1. Midnight City - M83 (played at 14:35:22)

> STATS
✓ Library: 2 tracks
✓ Relaxar: 0
✓ Focar: 2
✓ Animar: 0
✓ Treinar: 0

> EXIT
✓ Goodbye!
```

---

## 10. Delivery Phases

| Phase | Tasks | Deliverable |
|-------|-------|-------------|
| **Phase 1: Core CLI** | LineReader, CommandParser | Functional line-by-line input reader |
| **Phase 2: Dispatcher** | CommandExecutor, handler routing | All 10 menu commands executable |
| **Phase 3: Error Handling** | Exception hierarchy, validation | Robust error messages |
| **Phase 4: Testing** | Unit tests for parser, executor | `tests/test_cli.py` (pytest) |
| **Phase 5: Integration** | Refactor app.py to use CLI module | Single entry point `main.py` |
| **Phase 6: Documentation** | Help system, CLI guide | `CLI_GUIDE.md` for end users |

---

## 11. Command Reference (Help Output)

```
Available Commands:

  ADD <titulo> <artista> <genero> <bpm>
    Add a new track to the library.
    Example: ADD "Song Name" "Artist" "Pop" 120

  REMOVE <id>
    Remove track from library by ID.
    Example: REMOVE 5

  SEARCH <titulo|id>
    Search track by title or ID.
    Example: SEARCH "Song" or SEARCH 3

  LIST
    Display all tracks in library.

  REBUILD
    Rebuild mood queues from current library.

  QUEUE <mood>
    Show tracks in mood queue: Relaxar, Focar, Animar, Treinar
    Example: QUEUE Relaxar

  PLAY
    Play next track from current queue (dequeue + add to history).

  HISTORY
    Display playback history.

  STATS
    Display library and queue statistics.

  EXIT
    Terminate CLI session.
```

---

## 12. Configuration & Environment

### 12.1 CLI Settings (env vars / config file)

```python
# cli_config.py
import os

class CLIConfig:
    # Input/Output
    PROMPT = os.getenv('CLI_PROMPT', '> ')
    OUTPUT_ENCODING = os.getenv('CLI_ENCODING', 'utf-8')
    
    # Behavior
    CASE_SENSITIVE = os.getenv('CLI_CASE_SENSITIVE', 'false').lower() == 'true'
    MAX_HISTORY_LENGTH = int(os.getenv('CLI_MAX_HISTORY', '100'))
    
    # Logging
    LOG_COMMANDS = os.getenv('CLI_LOG_COMMANDS', 'false').lower() == 'true'
    LOG_FILE = os.getenv('CLI_LOG_FILE', '/tmp/playlist_cli.log')
```

---

## 13. Testing Strategy

### 13.1 Unit Tests (pytest)

```python
# tests/test_cli.py

import pytest
from cli import CommandParser, CommandExecutor, MenuOption

def test_parser_add_command():
    """Valid ADD command with 4 params."""
    cmd, params = CommandParser.parse_line('ADD Song Artist Pop 100')
    assert cmd == MenuOption.ADD
    assert params == ['Song', 'Artist', 'Pop', '100']

def test_parser_invalid_bpm():
    """ADD with non-integer BPM."""
    with pytest.raises(ValueError):
        CommandParser.parse_line('ADD Song Artist Pop notabpm')

def test_executor_add_track():
    """Executor successfully adds track."""
    sistema = SistemaPlaylist()
    executor = CommandExecutor(sistema)
    output = executor.execute(MenuOption.ADD, ['Song', 'Artist', 'Pop', '100'])
    assert '✓' in output
    assert 'Song' in output
```

---

## Conclusion

This CLI module provides a robust **line-by-line input processor** architecture for the music playlist system. It decouples input reading from command parsing and execution, making the system testable, extensible, and easy to integrate with future layers (REST API, batch processing, automation scripts).

**Key Design Principles**:
- Single Responsibility: Reader ≠ Parser ≠ Executor
- Fail-Safe: All errors caught and formatted for user
- Testable: Each component independently mockable
- Extensible: New commands added by extending MenuOption + handlers dict
- Reusable: CLI, BatchProcessor, and (future) REST API all use same CommandExecutor
