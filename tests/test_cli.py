"""
Unit tests for the CLI module.

This test suite validates:
- LineReader: Input stream processing
- CommandParser: Command parsing and validation
- CommandExecutor: Command dispatch and execution
- Error handling and edge cases
"""

import pytest
from cli import (
    LineReader,
    CommandParser,
    CommandExecutor,
    MenuOption,
    ParseError,
    ValidationError,
    StateError,
)
from app import SistemaPlaylist


class TestCommandParser:
    """Tests for CommandParser class."""

    def test_parse_valid_add_command(self):
        """Valid ADD command with 4 params should parse successfully."""
        cmd, params = CommandParser.parse_line('ADD Song Artist Pop 100')
        assert cmd == MenuOption.ADD
        assert params == ['Song', 'Artist', 'Pop', '100']

    def test_parse_add_with_quoted_strings(self):
        """ADD command with quoted parameters should handle spaces."""
        cmd, params = CommandParser.parse_line('ADD "My Song" "Artist Name" "Pop Mix" 120')
        assert cmd == MenuOption.ADD
        assert params == ['My Song', 'Artist Name', 'Pop Mix', '120']

    def test_parse_list_command(self):
        """LIST command requires no parameters."""
        cmd, params = CommandParser.parse_line('LIST')
        assert cmd == MenuOption.LIST
        assert params == []

    def test_parse_case_insensitive(self):
        """Commands should be case-insensitive."""
        cmd1, _ = CommandParser.parse_line('list')
        cmd2, _ = CommandParser.parse_line('LIST')
        cmd3, _ = CommandParser.parse_line('List')
        assert cmd1 == cmd2 == cmd3 == MenuOption.LIST

    def test_parse_invalid_command(self):
        """Invalid command should raise ParseError."""
        with pytest.raises(ParseError):
            CommandParser.parse_line('INVALID_COMMAND')

    def test_parse_empty_line(self):
        """Empty line should raise ParseError."""
        with pytest.raises(ParseError):
            CommandParser.parse_line('')

    def test_parse_add_missing_params(self):
        """ADD with insufficient params should raise ParseError."""
        with pytest.raises(ParseError):
            CommandParser.parse_line('ADD Song Artist')

    def test_parse_search_with_id(self):
        """SEARCH command should accept single param."""
        cmd, params = CommandParser.parse_line('SEARCH 42')
        assert cmd == MenuOption.SEARCH
        assert params == ['42']

    def test_parse_queue_with_mood(self):
        """QUEUE command should accept mood parameter."""
        cmd, params = CommandParser.parse_line('QUEUE Focar')
        assert cmd == MenuOption.QUEUE
        assert params == ['Focar']

    def test_parse_help_command(self):
        """HELP command should parse without params."""
        cmd, params = CommandParser.parse_line('HELP')
        assert cmd == MenuOption.HELP
        assert params == []


class TestCommandExecutor:
    """Tests for CommandExecutor class."""

    @pytest.fixture
    def executor(self):
        """Create a fresh executor with empty sistema for each test."""
        sistema = SistemaPlaylist()
        return CommandExecutor(sistema)

    def test_execute_add_valid_track(self, executor):
        """Execute ADD command with valid params."""
        result = executor.execute(
            MenuOption.ADD, ['Song', 'Artist', 'Genre', '100']
        )
        assert '✓' in result
        assert 'Track added' in result

    def test_execute_add_invalid_bpm(self, executor):
        """Execute ADD command with invalid BPM."""
        result = executor.execute(
            MenuOption.ADD, ['Song', 'Artist', 'Genre', 'not_a_number']
        )
        assert '✗' in result
        assert 'positive integer' in result

    def test_execute_add_zero_bpm(self, executor):
        """Execute ADD command with BPM = 0."""
        result = executor.execute(
            MenuOption.ADD, ['Song', 'Artist', 'Genre', '0']
        )
        assert '✗' in result
        assert 'BPM' in result and '0' in result

    def test_execute_add_negative_bpm(self, executor):
        """Execute ADD command with negative BPM."""
        result = executor.execute(
            MenuOption.ADD, ['Song', 'Artist', 'Genre', '-50']
        )
        assert '✗' in result

    def test_execute_list_empty_library(self, executor):
        """LIST command on empty library."""
        result = executor.execute(MenuOption.LIST, [])
        assert '✓' in result
        assert 'empty' in result.lower()

    def test_execute_list_with_tracks(self, executor):
        """LIST command with tracks in library."""
        executor.execute(MenuOption.ADD, ['Song1', 'Artist1', 'Pop', '100'])
        executor.execute(MenuOption.ADD, ['Song2', 'Artist2', 'Rock', '120'])
        result = executor.execute(MenuOption.LIST, [])
        assert '✓' in result
        assert 'Song1' in result
        assert 'Song2' in result

    def test_execute_rebuild(self, executor):
        """REBUILD command should rebuild queues."""
        executor.execute(MenuOption.ADD, ['Song', 'Artist', 'Genre', '100'])
        result = executor.execute(MenuOption.REBUILD, [])
        assert '✓' in result
        assert 'rebuilt' in result.lower()

    def test_execute_stats(self, executor):
        """STATS command should show statistics."""
        executor.execute(MenuOption.ADD, ['Song1', 'Artist', 'Genre', '70'])   # Relaxar
        executor.execute(MenuOption.ADD, ['Song2', 'Artist', 'Genre', '100'])  # Focar
        result = executor.execute(MenuOption.STATS, [])
        assert '✓' in result
        assert 'Library' in result
        assert 'Relaxar' in result
        assert 'Focar' in result

    def test_execute_search_by_id(self, executor):
        """SEARCH command by ID."""
        executor.execute(MenuOption.ADD, ['Song', 'Artist', 'Genre', '100'])
        result = executor.execute(MenuOption.SEARCH, ['1'])
        assert '✓' in result
        assert 'Song' in result

    def test_execute_search_by_title(self, executor):
        """SEARCH command by title."""
        executor.execute(MenuOption.ADD, ['My Song', 'Artist', 'Genre', '100'])
        result = executor.execute(MenuOption.SEARCH, ['My Song'])
        assert '✓' in result
        assert 'My Song' in result

    def test_execute_search_not_found(self, executor):
        """SEARCH command with non-existent track."""
        result = executor.execute(MenuOption.SEARCH, ['NonExistent'])
        assert '✗' in result

    def test_execute_queue_valid_mood(self, executor):
        """QUEUE command with valid mood."""
        executor.execute(MenuOption.ADD, ['Song', 'Artist', 'Genre', '100'])
        executor.execute(MenuOption.REBUILD, [])
        result = executor.execute(MenuOption.QUEUE, ['Focar'])
        assert '✓' in result
        assert 'Focar' in result

    def test_execute_queue_invalid_mood(self, executor):
        """QUEUE command with invalid mood."""
        result = executor.execute(MenuOption.QUEUE, ['InvalidMood'])
        assert '✗' in result
        assert 'Invalid mood' in result

    def test_execute_remove_valid_id(self, executor):
        """REMOVE command with valid ID."""
        executor.execute(MenuOption.ADD, ['Song', 'Artist', 'Genre', '100'])
        result = executor.execute(MenuOption.REMOVE, ['1'])
        assert '✓' in result
        assert 'removed' in result.lower()

    def test_execute_remove_invalid_id(self, executor):
        """REMOVE command with non-existent ID."""
        result = executor.execute(MenuOption.REMOVE, ['999'])
        assert '✗' in result
        assert 'not found' in result.lower()

    def test_execute_remove_non_integer(self, executor):
        """REMOVE command with non-integer ID."""
        result = executor.execute(MenuOption.REMOVE, ['not_an_id'])
        assert '✗' in result
        assert 'integer' in result

    def test_execute_play_empty_queue(self, executor):
        """PLAY command with no tracks."""
        result = executor.execute(MenuOption.PLAY, [])
        assert '✗' in result
        assert 'available' in result.lower()

    def test_execute_play_with_track(self, executor):
        """PLAY command with available track."""
        executor.execute(MenuOption.ADD, ['Song', 'Artist', 'Genre', '100'])
        executor.execute(MenuOption.REBUILD, [])
        result = executor.execute(MenuOption.PLAY, [])
        assert '✓' in result
        assert 'Now playing' in result

    def test_execute_history_empty(self, executor):
        """HISTORY command on empty history."""
        result = executor.execute(MenuOption.HISTORY, [])
        assert '✓' in result
        assert 'empty' in result.lower()

    def test_execute_history_with_tracks(self, executor):
        """HISTORY command after playing tracks."""
        executor.execute(MenuOption.ADD, ['Song', 'Artist', 'Genre', '100'])
        executor.execute(MenuOption.REBUILD, [])
        executor.execute(MenuOption.PLAY, [])
        result = executor.execute(MenuOption.HISTORY, [])
        assert '✓' in result
        assert 'Song' in result

    def test_execute_help(self, executor):
        """HELP command should return help text."""
        result = executor.execute(MenuOption.HELP, [])
        assert '✓' in result
        assert 'Available Commands' in result
        assert 'ADD' in result


class TestIntegration:
    """Integration tests for complete workflows."""

    def test_complete_workflow(self):
        """Test a complete workflow: add, rebuild, play, history."""
        sistema = SistemaPlaylist()
        executor = CommandExecutor(sistema)

        # Add tracks
        executor.execute(MenuOption.ADD, ['Relaxing' , 'Art1', 'Chill', '60'])
        executor.execute(MenuOption.ADD, ['Focusing', 'Art2', 'Work', '110'])
        executor.execute(MenuOption.ADD, ['Energetic', 'Art3', 'Dance', '140'])

        # Rebuild
        result = executor.execute(MenuOption.REBUILD, [])
        assert '✓' in result

        # Check stats
        result = executor.execute(MenuOption.STATS, [])
        assert 'Library: 3 tracks' in result

        # Play tracks
        play1 = executor.execute(MenuOption.PLAY, [])
        assert 'Now playing' in play1
        
        play2 = executor.execute(MenuOption.PLAY, [])
        assert 'Now playing' in play2

        # Check history
        history = executor.execute(MenuOption.HISTORY, [])
        assert 'Playback history (2 tracks)' in history

    def test_bpm_classification(self):
        """Test BPM classification into moods."""
        sistema = SistemaPlaylist()
        executor = CommandExecutor(sistema)

        # Add tracks with different BPMs
        executor.execute(MenuOption.ADD, ['Relaxar', 'A', 'G', '50'])   # Relaxar <= 80
        executor.execute(MenuOption.ADD, ['Focar', 'A', 'G', '100'])    # Focar 81-120
        executor.execute(MenuOption.ADD, ['Animar', 'A', 'G', '140'])   # Animar 121-160
        executor.execute(MenuOption.ADD, ['Treinar', 'A', 'G', '180'])  # Treinar > 160

        executor.execute(MenuOption.REBUILD, [])

        # Check each queue
        r1 = executor.execute(MenuOption.QUEUE, ['Relaxar'])
        r2 = executor.execute(MenuOption.QUEUE, ['Focar'])
        r3 = executor.execute(MenuOption.QUEUE, ['Animar'])
        r4 = executor.execute(MenuOption.QUEUE, ['Treinar'])

        assert '1 tracks' in r1  # Relaxar has 1 track
        assert '1 tracks' in r2  # Focar has 1 track
        assert '1 tracks' in r3  # Animar has 1 track
        assert '1 tracks' in r4  # Treinar has 1 track


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
