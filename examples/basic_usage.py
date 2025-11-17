"""
Basic Usage Example for Chess Engine.

This example demonstrates how to use the chess engine components
programmatically without the GUI.
"""

import chess
from src.chess_engine.board_manager import BoardManager
from src.chess_engine.threat_analyzer import ThreatAnalyzer
from src.chess_engine.move_suggester import MoveSuggester


def example_basic_moves():
    """
    Example 1: Basic board setup and move making.
    
    Demonstrates initializing a board, making moves, and checking game state.
    """
    print("=" * 60)
    print("Example 1: Basic Moves")
    print("=" * 60)
    
    # Create a new board with starting position
    board_manager = BoardManager()
    
    # Display initial position
    print("\nInitial Position:")
    print(board_manager)
    print(f"FEN: {board_manager.get_fen()}")
    
    # Make some opening moves (Italian Game)
    moves = ["e2e4", "e7e5", "g1f3", "b8c6", "f1c4"]
    
    print("\nMaking moves: 1. e4 e5 2. Nf3 Nc6 3. Bc4")
    for move_uci in moves:
        move = chess.Move.from_uci(move_uci)
        board_manager.make_move(move)
    
    # Display position after moves
    print("\nPosition after moves:")
    print(board_manager)
    print(f"Turn: {'White' if board_manager.get_turn() == chess.WHITE else 'Black'}")
    print(f"Legal moves available: {len(board_manager.get_legal_moves())}")


def example_threat_analysis():
    """
    Example 2: Threat analysis.
    
    Demonstrates analyzing threats and finding hanging pieces.
    """
    print("\n" + "=" * 60)
    print("Example 2: Threat Analysis")
    print("=" * 60)
    
    # Set up a position with some tactics
    board_manager = BoardManager()
    
    # Create a position where Black has a hanging knight
    fen = "r1bqkb1r/pppp1ppp/2n5/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4"
    board_manager.set_position_from_fen(fen)
    
    print("\nAnalyzing position:")
    print(board_manager)
    
    # Create threat analyzer
    threat_analyzer = ThreatAnalyzer(board_manager)
    
    # Get comprehensive analysis
    analysis = threat_analyzer.analyze_position()
    
    print(f"\nCurrent turn: {analysis['current_turn']}")
    print(f"Is check: {analysis['is_check']}")
    print(f"Is checkmate: {analysis['is_checkmate']}")
    
    # Check for hanging pieces
    white_hanging = analysis['white_hanging']
    black_hanging = analysis['black_hanging']
    
    print("\n--- Hanging Pieces ---")
    if white_hanging:
        print("White hanging pieces:")
        for threat in white_hanging:
            print(f"  - {threat}")
    else:
        print("No white hanging pieces")
    
    if black_hanging:
        print("\nBlack hanging pieces:")
        for threat in black_hanging:
            print(f"  - {threat}")
    else:
        print("No black hanging pieces")


def example_move_suggestions():
    """
    Example 3: Move suggestions with explanations.
    
    Demonstrates getting best move recommendations.
    """
    print("\n" + "=" * 60)
    print("Example 3: Move Suggestions")
    print("=" * 60)
    
    # Set up an interesting tactical position
    board_manager = BoardManager()
    
    # Position where White can win material
    fen = "r1bqkb1r/pppp1ppp/2n5/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4"
    board_manager.set_position_from_fen(fen)
    
    print("\nPosition to analyze:")
    print(board_manager)
    
    # Create move suggester
    move_suggester = MoveSuggester(board_manager)
    
    # Get best moves
    print("\n--- Top 3 Move Suggestions ---")
    best_moves = move_suggester.get_best_moves(num_moves=3)
    
    for i, move_eval in enumerate(best_moves, 1):
        print(f"\n{i}. Move: {move_eval.move.uci()}")
        print(f"   Score: {move_eval.score:.2f}")
        print(f"   Explanation: {move_eval.explanation}")
        if move_eval.tactical_themes:
            print(f"   Themes: {', '.join(move_eval.tactical_themes)}")


def main():
    """
    Run all examples.
    
    Executes all example functions to demonstrate chess engine capabilities.
    """
    print("\n" + "=" * 60)
    print("CHESS ENGINE USAGE EXAMPLES")
    print("=" * 60)
    
    # Run all examples
    example_basic_moves()
    example_threat_analysis()
    example_move_suggestions()
    
    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
