#!/usr/bin/env python3
"""
Simple test runner for CLI tests (no pytest required).
Run this with: python run_tests.py
"""

import sys
import traceback

sys.path.insert(0, '/workspaces/fatec-ed-playlist')

from cli import (
    CommandParser,
    CommandExecutor,
    MenuOption,
    ParseError,
)
from app import SistemaPlaylist


class TestRunner:
    """Simple test runner class."""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.total = 0
    
    def test(self, name, func):
        """Run a single test."""
        self.total += 1
        try:
            func()
            self.passed += 1
            print(f"✓ {name}")
        except AssertionError as e:
            self.failed += 1
            print(f"✗ {name}")
            print(f"  Error: {e}")
        except Exception as e:
            self.failed += 1
            print(f"✗ {name}")
            print(f"  Exception: {e}")
            traceback.print_exc()
    
    def summary(self):
        """Print test summary."""
        print(f"\n{'='*60}")
        print(f"Tests run: {self.total}")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        print(f"{'='*60}")
        return self.failed == 0


def main():
    """Run all tests."""
    runner = TestRunner()
    
    print("Running CLI Tests...\n")
    
    # ========================================================================
    # CommandParser Tests
    # ========================================================================
    print("CommandParser Tests:")
    
    def test_parse_valid_add():
        cmd, params = CommandParser.parse_line('ADD Song Artist Pop 100')
        assert cmd == MenuOption.ADD
        assert params == ['Song', 'Artist', 'Pop', '100']
    
    def test_parse_quoted_strings():
        cmd, params = CommandParser.parse_line('ADD "My Song" "Artist Name" "Pop" 120')
        assert cmd == MenuOption.ADD
        assert params == ['My Song', 'Artist Name', 'Pop', '120']
    
    def test_parse_list():
        cmd, params = CommandParser.parse_line('LIST')
        assert cmd == MenuOption.LIST
        assert params == []
    
    def test_parse_case_insensitive():
        cmd1, _ = CommandParser.parse_line('list')
        cmd2, _ = CommandParser.parse_line('LIST')
        assert cmd1 == cmd2 == MenuOption.LIST
    
    def test_parse_invalid_command():
        try:
            CommandParser.parse_line('INVALID')
            assert False, "Should raise ParseError"
        except ParseError:
            pass
    
    def test_parse_empty_line():
        try:
            CommandParser.parse_line('')
            assert False, "Should raise ParseError"
        except ParseError:
            pass
    
    def test_parse_insufficient_params():
        try:
            CommandParser.parse_line('ADD Song')
            assert False, "Should raise ParseError"
        except ParseError:
            pass
    
    runner.test("parse_valid_add", test_parse_valid_add)
    runner.test("parse_quoted_strings", test_parse_quoted_strings)
    runner.test("parse_list", test_parse_list)
    runner.test("parse_case_insensitive", test_parse_case_insensitive)
    runner.test("parse_invalid_command", test_parse_invalid_command)
    runner.test("parse_empty_line", test_parse_empty_line)
    runner.test("parse_insufficient_params", test_parse_insufficient_params)
    
    # ========================================================================
    # CommandExecutor Tests
    # ========================================================================
    print("\nCommandExecutor Tests:")
    
    def test_execute_add_valid():
        sistema = SistemaPlaylist()
        executor = CommandExecutor(sistema)
        result = executor.execute(MenuOption.ADD, ['Song', 'Artist', 'Genre', '100'])
        assert '✓' in result
        assert 'Track added' in result
    
    def test_execute_add_invalid_bpm():
        sistema = SistemaPlaylist()
        executor = CommandExecutor(sistema)
        result = executor.execute(MenuOption.ADD, ['Song', 'Artist', 'Genre', 'invalid'])
        assert '✗' in result
    
    def test_execute_add_zero_bpm():
        sistema = SistemaPlaylist()
        executor = CommandExecutor(sistema)
        result = executor.execute(MenuOption.ADD, ['Song', 'Artist', 'Genre', '0'])
        assert '✗' in result
    
    def test_execute_list_empty():
        sistema = SistemaPlaylist()
        executor = CommandExecutor(sistema)
        result = executor.execute(MenuOption.LIST, [])
        assert '✓' in result
        assert 'empty' in result.lower()
    
    def test_execute_list_with_tracks():
        sistema = SistemaPlaylist()
        executor = CommandExecutor(sistema)
        executor.execute(MenuOption.ADD, ['Song1', 'Artist1', 'Pop', '100'])
        executor.execute(MenuOption.ADD, ['Song2', 'Artist2', 'Rock', '120'])
        result = executor.execute(MenuOption.LIST, [])
        assert 'Song1' in result
        assert 'Song2' in result
    
    def test_execute_rebuild():
        sistema = SistemaPlaylist()
        executor = CommandExecutor(sistema)
        executor.execute(MenuOption.ADD, ['Song', 'Artist', 'Genre', '100'])
        result = executor.execute(MenuOption.REBUILD, [])
        assert '✓' in result
        assert 'rebuilt' in result.lower()
    
    def test_execute_stats():
        sistema = SistemaPlaylist()
        executor = CommandExecutor(sistema)
        executor.execute(MenuOption.ADD, ['S1', 'A', 'G', '70'])
        executor.execute(MenuOption.ADD, ['S2', 'A', 'G', '100'])
        result = executor.execute(MenuOption.STATS, [])
        assert 'Library' in result
        assert 'Relaxar' in result
    
    def test_execute_search_by_id():
        sistema = SistemaPlaylist()
        executor = CommandExecutor(sistema)
        executor.execute(MenuOption.ADD, ['Song', 'Artist', 'Genre', '100'])
        result = executor.execute(MenuOption.SEARCH, ['1'])
        assert 'Song' in result
    
    def test_execute_search_not_found():
        sistema = SistemaPlaylist()
        executor = CommandExecutor(sistema)
        result = executor.execute(MenuOption.SEARCH, ['NonExistent'])
        assert '✗' in result
    
    def test_execute_queue_valid():
        sistema = SistemaPlaylist()
        executor = CommandExecutor(sistema)
        executor.execute(MenuOption.ADD, ['Song', 'Artist', 'Genre', '100'])
        executor.execute(MenuOption.REBUILD, [])
        result = executor.execute(MenuOption.QUEUE, ['Focar'])
        assert 'Focar' in result
    
    def test_execute_queue_invalid():
        sistema = SistemaPlaylist()
        executor = CommandExecutor(sistema)
        result = executor.execute(MenuOption.QUEUE, ['InvalidMood'])
        assert '✗' in result
    
    def test_execute_remove_valid():
        sistema = SistemaPlaylist()
        executor = CommandExecutor(sistema)
        executor.execute(MenuOption.ADD, ['Song', 'Artist', 'Genre', '100'])
        result = executor.execute(MenuOption.REMOVE, ['1'])
        assert 'removed' in result.lower()
    
    def test_execute_remove_not_found():
        sistema = SistemaPlaylist()
        executor = CommandExecutor(sistema)
        result = executor.execute(MenuOption.REMOVE, ['999'])
        assert '✗' in result
    
    def test_execute_play():
        sistema = SistemaPlaylist()
        executor = CommandExecutor(sistema)
        executor.execute(MenuOption.ADD, ['Song', 'Artist', 'Genre', '100'])
        executor.execute(MenuOption.REBUILD, [])
        result = executor.execute(MenuOption.PLAY, [])
        assert 'Now playing' in result
    
    def test_execute_history():
        sistema = SistemaPlaylist()
        executor = CommandExecutor(sistema)
        executor.execute(MenuOption.ADD, ['Song', 'Artist', 'Genre', '100'])
        executor.execute(MenuOption.REBUILD, [])
        executor.execute(MenuOption.PLAY, [])
        result = executor.execute(MenuOption.HISTORY, [])
        assert 'Song' in result
    
    def test_execute_help():
        sistema = SistemaPlaylist()
        executor = CommandExecutor(sistema)
        result = executor.execute(MenuOption.HELP, [])
        assert 'Available Commands' in result
    
    runner.test("execute_add_valid", test_execute_add_valid)
    runner.test("execute_add_invalid_bpm", test_execute_add_invalid_bpm)
    runner.test("execute_add_zero_bpm", test_execute_add_zero_bpm)
    runner.test("execute_list_empty", test_execute_list_empty)
    runner.test("execute_list_with_tracks", test_execute_list_with_tracks)
    runner.test("execute_rebuild", test_execute_rebuild)
    runner.test("execute_stats", test_execute_stats)
    runner.test("execute_search_by_id", test_execute_search_by_id)
    runner.test("execute_search_not_found", test_execute_search_not_found)
    runner.test("execute_queue_valid", test_execute_queue_valid)
    runner.test("execute_queue_invalid", test_execute_queue_invalid)
    runner.test("execute_remove_valid", test_execute_remove_valid)
    runner.test("execute_remove_not_found", test_execute_remove_not_found)
    runner.test("execute_play", test_execute_play)
    runner.test("execute_history", test_execute_history)
    runner.test("execute_help", test_execute_help)
    
    # ========================================================================
    # Integration Tests
    # ========================================================================
    print("\nIntegration Tests:")
    
    def test_complete_workflow():
        sistema = SistemaPlaylist()
        executor = CommandExecutor(sistema)
        
        executor.execute(MenuOption.ADD, ['Relaxing', 'A1', 'Chill', '60'])
        executor.execute(MenuOption.ADD, ['Focusing', 'A2', 'Work', '110'])
        executor.execute(MenuOption.ADD, ['Energetic', 'A3', 'Dance', '140'])
        
        executor.execute(MenuOption.REBUILD, [])
        
        stats = executor.execute(MenuOption.STATS, [])
        assert 'Library: 3 tracks' in stats
        
        executor.execute(MenuOption.PLAY, [])
        executor.execute(MenuOption.PLAY, [])
        
        history = executor.execute(MenuOption.HISTORY, [])
        assert '2 tracks' in history
    
    def test_bpm_classification():
        sistema = SistemaPlaylist()
        executor = CommandExecutor(sistema)
        
        # Add tracks with specific BPMs
        executor.execute(MenuOption.ADD, ['R', 'A', 'G', '50'])   # Relaxar
        executor.execute(MenuOption.ADD, ['F', 'A', 'G', '100'])  # Focar
        executor.execute(MenuOption.ADD, ['An', 'A', 'G', '140']) # Animar
        executor.execute(MenuOption.ADD, ['T', 'A', 'G', '180'])  # Treinar
        
        executor.execute(MenuOption.REBUILD, [])
        
        # Check each queue has exactly 1 track
        r1 = executor.execute(MenuOption.QUEUE, ['Relaxar'])
        r2 = executor.execute(MenuOption.QUEUE, ['Focar'])
        r3 = executor.execute(MenuOption.QUEUE, ['Animar'])
        r4 = executor.execute(MenuOption.QUEUE, ['Treinar'])
        
        assert '1 tracks' in r1
        assert '1 tracks' in r2
        assert '1 tracks' in r3
        assert '1 tracks' in r4
    
    runner.test("complete_workflow", test_complete_workflow)
    runner.test("bpm_classification", test_bpm_classification)
    
    # ========================================================================
    # Print summary
    # ========================================================================
    success = runner.summary()
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
