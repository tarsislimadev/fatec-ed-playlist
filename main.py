#!/usr/bin/env python3
"""
Main entry point for the Playlist application.

Supports two modes:
- Interactive CLI: `python main.py`
- Demo mode: `python main.py --demo`
"""

import sys
from app import SistemaPlaylist, executar_demo
from cli import REPL


def main():
    """Main entry point."""
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        executar_demo()
        return

    try:
        sistema = SistemaPlaylist()
        repl = REPL(sistema)
        repl.run()
    except KeyboardInterrupt:
        print("\n✗ Interrupted")
        sys.exit(1)
    except EOFError:
        print("\n✓ EOF reached - Goodbye!")
        sys.exit(0)


if __name__ == "__main__":
    main()
