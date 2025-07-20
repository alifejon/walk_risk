"""
Main entry point for Walk Risk game
"""
import sys
from walk_risk.ui.cli import cli


if __name__ == "__main__":
    # Run CLI interface
    sys.argv[0] = "walk-risk"
    cli()