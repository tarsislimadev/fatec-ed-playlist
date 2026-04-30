"""
CLI - Line-by-Line Input Application for Playlist System

This module provides a complete Command Line Interface with:
- LineReader: input stream processing
- CommandParser: command tokenization and validation
- CommandExecutor: command dispatch to SistemaPlaylist
- REPL: interactive read-eval-print loop
"""

import sys
import shlex
from enum import Enum
from typing import Callable, Dict, Iterator, List, Optional, Tuple


# =============================================================================
# Exception Hierarchy
# =============================================================================

class CLIException(Exception):
    """Base exception for CLI errors."""
    pass


class ParseError(CLIException):
    """Raised when input cannot be parsed."""
    pass


class ValidationError(CLIException):
    """Raised when params fail validation."""
    pass


class StateError(CLIException):
    """Raised when domain state is invalid."""
    pass


# =============================================================================
# LineReader - Input Stream Processing
# =============================================================================

class LineReader:
    """Reads and buffers input lines from stdin."""

    def __init__(self, buffer_size: int = 1024):
        """
        Initialize LineReader.
        
        Args:
            buffer_size: Maximum buffer size (not strictly enforced)
        """
        self.buffer_size = buffer_size
        self.line_count = 0

    def read_line(self) -> Optional[str]:
        """
        Read a single line from stdin, strip whitespace.

        Returns:
            str: Line content
            None: EOF reached
            
        Raises:
            KeyboardInterrupt: If Ctrl+C is pressed
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


# =============================================================================
# CommandParser - Command Tokenization and Validation
# =============================================================================

class MenuOption(Enum):
    """Enumeration of all CLI commands."""
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
    HELP = "HELP"


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
            ParseError: If command invalid or params missing
        """
        try:
            tokens = CommandParser._parse_quoted_params(line)
        except Exception as e:
            raise ParseError(f"Syntax error: {str(e)}")

        if not tokens:
            raise ParseError("Empty command")

        command_str = tokens[0].upper()
        if command_str not in CommandParser.COMMAND_MAP:
            raise ParseError(f"Unknown command: {command_str}")

        menu_opt = CommandParser.COMMAND_MAP[command_str]
        params = tokens[1:]

        # Validate param count
        required_params = CommandParser._get_param_count(menu_opt)
        if len(params) < required_params:
            raise ParseError(
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
            MenuOption.HELP: 0,
        }
        return rules.get(opt, 999)  # Default: require all

    @staticmethod
    def _parse_quoted_params(line: str) -> List[str]:
        """
        Parse params respecting quoted strings.

        Example:
            input:  ADD "My Song" Artist Pop 120
            output: ['ADD', 'My Song', 'Artist', 'Pop', '120']

        Args:
            line: Raw input line

        Returns:
            List of tokens

        Raises:
            ParseError: If quote mismatch
        """
        try:
            return shlex.split(line)
        except ValueError as e:
            raise ParseError(f"Unmatched quotes: {str(e)}")


# =============================================================================
# CommandExecutor - Command Dispatch to SistemaPlaylist
# =============================================================================

class CommandExecutor:
    """
    Dispatches parsed commands to SistemaPlaylist methods.
    Maps MenuOption → handler function.
    """

    def __init__(self, sistema):
        """
        Initialize CommandExecutor.
        
        Args:
            sistema: SistemaPlaylist instance
        """
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
            MenuOption.HELP: self._handle_help,
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

        except ValidationError as e:
            return f"✗ Validation failed: {str(e)}"
        except StateError as e:
            return f"✗ Invalid state: {str(e)}"
        except ParseError as e:
            return f"✗ Parse error: {str(e)}"
        except ValueError as e:
            return f"✗ Invalid params: {str(e)}"
        except Exception as e:
            return f"✗ Error: {str(e)}"

    # =========================================================================
    # Handler Methods
    # =========================================================================

    def _handle_add(self, titulo: str, artista: str, genero: str, bpm: str) -> str:
        """ADD titulo artista genero bpm"""
        try:
            bpm_int = int(bpm)
            if bpm_int <= 0:
                raise ValueError("BPM must be > 0")
            musica = self.sistema.adicionar_musica(titulo, artista, genero, bpm_int)
            return f"Track added: {musica.titulo} (ID: {musica.id}, {bpm_int} BPM)"
        except ValueError as e:
            if "BPM" in str(e):
                raise
            raise ValueError("BPM must be a positive integer")

    def _handle_remove(self, track_id: str) -> str:
        """REMOVE id"""
        try:
            track_id_int = int(track_id)
            musica = self.sistema.remover_musica(track_id_int)
            if musica is None:
                raise StateError(f"Track {track_id_int} not found")
            return f"Track {track_id_int} removed: {musica.titulo}"
        except ValueError:
            raise ValueError("ID must be an integer")

    def _handle_search(self, query: str) -> str:
        """SEARCH titulo|id"""
        # Try ID first
        try:
            track_id = int(query)
            track = self.sistema.biblioteca.buscar_por_id(track_id)
            if track:
                return self._format_track(track)
            raise StateError(f"Track {track_id} not found by ID")
        except ValueError:
            pass

        # Try title
        track = self.sistema.biblioteca.buscar_por_titulo(query)
        if track:
            return self._format_track(track)
        raise StateError(f"Track '{query}' not found by title")

    def _handle_list(self) -> str:
        """LIST"""
        tracks = list(self.sistema.biblioteca.iterar())
        if not tracks:
            return "Library is empty"
        return "Library:\n" + "\n".join(self._format_track(t) for t in tracks)

    def _handle_rebuild(self) -> str:
        """REBUILD"""
        self.sistema.reconstruir_filas_humor()
        stats = self._get_queue_stats()
        return f"Queues rebuilt: {stats}"

    def _handle_queue(self, mood_name: str) -> str:
        """QUEUE mood_name"""
        mood = mood_name.capitalize()
        if mood not in self.sistema.filas_humor:
            valid_moods = ", ".join(self.sistema.filas_humor.keys())
            raise ValidationError(f"Invalid mood. Valid moods: {valid_moods}")

        fila = self.sistema.obter_fila(mood)
        tracks = list(fila.iterar())
        
        if not tracks:
            return f"Queue '{mood}' is empty"
        
        result = f"Queue '{mood}' ({len(tracks)} tracks):\n"
        result += "\n".join(self._format_track(t) for t in tracks)
        return result

    def _handle_play(self) -> str:
        """PLAY"""
        # Try to play from Focar queue first, then check other queues
        moods_order = ["Focar", "Relaxar", "Animar", "Treinar"]
        musica = None
        mood_played = None

        for mood in moods_order:
            fila = self.sistema.obter_fila(mood)
            if fila.tamanho > 0:
                musica = self.sistema.reproduzir_proxima(mood)
                mood_played = mood
                break

        if musica is None:
            raise StateError("No tracks available to play")

        return f"Now playing: {musica.titulo} by {musica.artista} (from {mood_played})"

    def _handle_history(self) -> str:
        """HISTORY"""
        tracks = list(self.sistema.historico.iterar())
        if not tracks:
            return "Playback history is empty"

        result = f"Playback history ({len(tracks)} tracks):\n"
        for idx, track in enumerate(tracks, 1):
            result += f"{idx}. {track.titulo} - {track.artista}\n"
        return result.rstrip()

    def _handle_stats(self) -> str:
        """STATS"""
        total = self.sistema.biblioteca.tamanho
        result = f"Library: {total} tracks\n"
        
        for humor in self.sistema.filas_humor:
            count = self.sistema.filas_humor[humor].tamanho
            result += f"{humor}: {count}\n"
        
        result += f"History: {self.sistema.historico.tamanho} plays"
        return result

    def _handle_exit(self) -> str:
        """EXIT"""
        raise SystemExit(0)

    def _handle_help(self) -> str:
        """HELP"""
        help_text = """
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
    Play next track (dequeue + add to history).

  HISTORY
    Display playback history.

  STATS
    Display library and queue statistics.

  HELP
    Show this help message.

  EXIT
    Terminate CLI session.
"""
        return help_text.strip()

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def _format_track(self, track) -> str:
        """Format track for display."""
        return f"[{track.id}] {track.titulo} - {track.artista} ({track.bpm} BPM, {track.genero})"

    def _format_success(self, msg: str) -> str:
        """Wrap success message with ✓ indicator."""
        return f"✓ {msg}" if msg and not msg.startswith("✗") else msg

    def _get_queue_stats(self) -> str:
        """Get queue statistics for display."""
        stats = []
        for humor in self.sistema.filas_humor:
            count = self.sistema.filas_humor[humor].tamanho
            stats.append(f"{humor}={count}")
        return ", ".join(stats)


# =============================================================================
# REPL - Read-Eval-Print Loop
# =============================================================================

class REPL:
    """
    Read-Eval-Print Loop: continuously reads commands,
    executes them, and prints results.
    """

    def __init__(self, sistema):
        """
        Initialize REPL.
        
        Args:
            sistema: SistemaPlaylist instance
        """
        self.reader = LineReader()
        self.parser = CommandParser()
        self.executor = CommandExecutor(sistema)

    def run(self):
        """Main REPL loop."""
        print("🎵 Playlist CLI - Type 'HELP' for commands or 'EXIT' to quit")
        print()

        try:
            for line in self.reader.read_lines():
                try:
                    cmd, params = self.parser.parse_line(line)

                    if cmd == MenuOption.EXIT:
                        print("✓ Goodbye!")
                        break

                    output = self.executor.execute(cmd, params)
                    print(output)
                    print()

                except ParseError as e:
                    print(f"✗ Parse error: {str(e)}")
                    print()
                except KeyboardInterrupt:
                    print("\n✗ Interrupted")
                    break
                except SystemExit:
                    print("✓ Goodbye!")
                    break
                except Exception as e:
                    print(f"✗ Unexpected error: {str(e)}")
                    print()

        except KeyboardInterrupt:
            print("\n✗ Interrupted")
        except EOFError:
            print("\n✓ EOF reached - Goodbye!")


# =============================================================================
# Batch Mode - Execute commands from file
# =============================================================================

def run_batch(sistema, filepath: str):
    """
    Execute commands from a file (one per line).
    Useful for testing and automation.

    Args:
        sistema: SistemaPlaylist instance
        filepath: Path to command file

    Raises:
        FileNotFoundError: If file not found
    """
    parser = CommandParser()
    executor = CommandExecutor(sistema)

    try:
        with open(filepath, "r") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith("#"):  # Skip comments and blanks
                    continue

                try:
                    cmd, params = parser.parse_line(line)
                    if cmd == MenuOption.EXIT:
                        break
                    output = executor.execute(cmd, params)
                    print(f"[Line {line_num}] {output}")
                except SystemExit:
                    break
                except Exception as e:
                    print(f"[Line {line_num}] ✗ Error: {str(e)}")

    except FileNotFoundError:
        print(f"✗ File not found: {filepath}")


if __name__ == "__main__":
    # This module is meant to be imported and used, not run directly
    print("This is a CLI module. Import it into your application.")
