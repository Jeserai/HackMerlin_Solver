#!/usr/bin/env python3
"""
Main entry point for HackMerlin Solver.

This script provides the command-line interface for the HackMerlin Solver package.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from hackmerlin import HackMerlinSolver


def main():
    """Main entry point with command line argument support."""
    import argparse
    
    parser = argparse.ArgumentParser(description='HackMerlin Solver')
    parser.add_argument('--resource-level', choices=['low', 'medium', 'high'], 
                       default='low', help='Resource level for AI capabilities')
    parser.add_argument('--playwright', choices=['yes', 'no'], 
                       default='no', help='Use Playwright automation (yes) or manual mode (no)')
    args = parser.parse_args()
    
    # Convert playwright argument to boolean
    use_playwright = args.playwright == 'yes'
    
    solver = HackMerlinSolver(resource_level=args.resource_level, use_playwright=use_playwright)
    try:
        solver.run()
    except KeyboardInterrupt:
        print("Interrupted")


if __name__ == "__main__":
    main()
