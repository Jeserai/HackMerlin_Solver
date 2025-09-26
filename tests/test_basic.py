"""
Basic tests for HackMerlin Solver package.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from hackmerlin import HackMerlinSolver, GameAutomation, PromptGenerator, ResponseParser


def test_imports():
    """Test that all main components can be imported."""
    assert HackMerlinSolver is not None
    assert GameAutomation is not None
    assert PromptGenerator is not None
    assert ResponseParser is not None


def test_solver_initialization():
    """Test that HackMerlinSolver can be initialized."""
    solver = HackMerlinSolver(resource_level='low', use_playwright=False)
    assert solver is not None
    assert solver.game_automation is not None
    assert solver.resource_manager is not None


def test_game_automation_initialization():
    """Test that GameAutomation can be initialized."""
    automation = GameAutomation(use_playwright=False)
    assert automation is not None
    assert automation.manual_mode is True


if __name__ == "__main__":
    test_imports()
    test_solver_initialization()
    test_game_automation_initialization()
    print("✅ All basic tests passed!")
