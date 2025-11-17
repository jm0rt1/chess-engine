# Copilot instructions for this repo

Purpose: Help AI coding agents be productive quickly in this chess engine + computer vision project. Keep changes aligned with the existing architecture and workflows below.

## Big picture
- Entry points:
  - Tkinter app: `run.py` -> `src/main.py` -> `src/gui/chess_app.py`.
  - PySide6 app: `run_pyside6.py` -> `src/gui_pyside6/main_window.py`.
- Core modules (OOP, SOLID-ish separation):
  - `src/chess_engine/`: chess logic. `BoardManager` (board state/moves), `ThreatAnalyzer` (threats, hanging pieces, checks), `MoveSuggester` (simple eval + suggested moves with explanations).
  - `src/computer_vision/`: image pipeline. `BoardDetector` (detect board, segment 8×8), `PieceRecognizer` (heuristic recognition → FEN with confidences).
  - GUI layers:
    - Tkinter: `src/gui/chess_app.py` tabs for board state, threats, best moves.
    - PySide6: `src/gui_pyside6/` with widgets for pipeline, board, analysis; signal/slot wiring in `main_window.py`.
  - Shared config: `src/shared/settings.py` creates `./output/logs/{global,ui}`.
- Data flow (CV → engine → UI): image → detect board → split into squares → recognize pieces → FEN → `BoardManager.set_position_from_fen` → `ThreatAnalyzer`/`MoveSuggester` → GUI renders text/graphics.

## Developer workflows
- Environment
  - Create venv and install deps: `./init-venv.sh` then `pip install -r requirements.txt`.
  - GUI deps: Tk (tkinter) required; PySide6 may need system GL libs on Linux (see `PYSIDE6_GUI_README.md`).
- Run
  - Tkinter GUI: `python run.py` (initializes logging and launches GUI).
  - PySide6 GUI (recommended visualization): `python run_pyside6.py`.
  - CLI example usage: `python examples/basic_usage.py`.
- Tests
  - Fast path: `./test.sh` (unittest discovery).
  - PyTest alternative: `python -m pytest tests/ -v` (GUI tests skip in headless or missing PySide6).
- Debugging
  - Logs written to `output/logs/global/global.log` (rotating, configured in `src/main.py` + `src/shared/settings.py`).
  - CV stages are rendered in the PySide6 pipeline widget; use it to inspect failures in detection/recognition.

## Conventions and patterns
- Package layout assumes repo root on `sys.path`; scripts import via `from src...`. Keep new code under `src/` with `__init__.py`.
- Prefer absolute imports rooted at `src` (e.g., `from src.chess_engine.board_manager import BoardManager`).
- GUI separation:
  - Don’t put chess or CV logic in widgets; keep logic in `src/chess_engine` and `src/computer_vision`, and pass results to UI.
  - PySide6 uses QGraphicsScene for drawing; follow existing color/legend conventions in `widgets/analysis_widget.py` and `board_widget.py`.
- Engine evaluation is intentionally simple and explainable; when extending, keep `MoveEvaluation` explanations/tactical themes populated.
- CV recognition is heuristic (no ML). Respect `PieceRecognizer.min_confidence`; if below, prefer returning unknown/EMPTY and surface confidence to the UI.
- Logging: use module-level `logging.getLogger(__name__)`; avoid printing in library code.

## Integration points
- `BoardDetector.detect_board(image)` returns `(board_image, squares)`; `squares` is 8×8 of NumPy arrays (row 0 = rank 8). `PieceRecognizer.results_to_fen(results)` builds FEN consumed by `BoardManager`.
- `ThreatAnalyzer.analyze_position()` returns a dict consumed by UIs; `get_threat_summary()` provides human-readable text.
- `MoveSuggester.get_best_moves(num_moves)` returns `List[MoveEvaluation]` used by UIs; keep scores in centipawns and explanations concise.

## When adding features
- Put new analysis in `src/chess_engine` with clear APIs, then render in both GUIs if user-facing.
- For PySide6 visuals, add a widget under `src/gui_pyside6/widgets/` and wire it in `main_window.py` via signals/slots.
- Provide a minimal example in `examples/` and at least one unit test under `tests/` (GUI tests may be import-only/skipped in headless).

References: `CHESS_ENGINE_README.md`, `QUICK_START.md`, `PYSIDE6_GUI_README.md`, `PYSIDE6_IMPLEMENTATION_SUMMARY.md`.
