# PySide6 GUI Architecture Diagram

## System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Chess Engine Project                         │
│                        PySide6 GUI Application                        │
└─────────────────────────────────────────────────────────────────────┘

                              ┌──────────────┐
                              │  run_pyside6 │
                              │    .py       │
                              └──────┬───────┘
                                     │
                                     ▼
                     ┌───────────────────────────┐
                     │      MainWindow           │
                     │   (main_window.py)        │
                     │                           │
                     │  • Menu Bar & Shortcuts   │
                     │  • Layout Management      │
                     │  • Event Coordination     │
                     │  • Status Bar             │
                     └────┬───────────────┬──────┘
                          │               │
         ┌────────────────┴─────┐   ┌────┴───────────────┐
         │                      │   │                    │
         ▼                      ▼   ▼                    ▼
┌────────────────┐    ┌──────────────────────┐   ┌─────────────┐
│ ControlPanel   │    │  PipelineWidget      │   │  TabWidget  │
│ Widget         │    │                      │   └──────┬──────┘
│                │    │  • 6 Processing      │          │
│ • Load Image   │    │    Stages Display    │   ┌──────┴──────┐
│ • Process      │    │  • Step Navigation   │   │             │
│ • Step Through │    │  • Stage Selector    │   ▼             ▼
│ • Analyze      │    │  • Grid Layout       │  ┌──────┐  ┌──────────┐
│ • Reset        │    │                      │  │Board │  │ Analysis │
│ • FEN Entry    │    │ Stage 1: Raw Image   │  │Widget│  │ Widget   │
└────────────────┘    │ Stage 2: Preprocess  │  └──────┘  └──────────┘
                      │ Stage 3: Edges       │
                      │ Stage 4: Board       │
                      │ Stage 5: Squares     │
                      │ Stage 6: Pieces      │
                      └──────────────────────┘
```

## Widget Details

### BoardReconstructionWidget
```
┌────────────────────────────────────────────────┐
│          Board Reconstruction Widget           │
├────────────────────────────────────────────────┤
│  ┌──────────────────┐  ┌──────────────────┐   │
│  │  Chess Board     │  │  Information     │   │
│  │  Graphics Scene  │  │  Panel           │   │
│  │                  │  │                  │   │
│  │  ♜ ♞ ♝ ♛ ♚ ♝ ♞ ♜  │  │  FEN: rnb...   │   │
│  │  ♟ ♟ ♟ ♟ ♟ ♟ ♟ ♟  │  │                  │   │
│  │  . . . . . . . .  │  │  Turn: White    │   │
│  │  . . . . . . . .  │  │  Status: Normal │   │
│  │  . . . . . . . .  │  │                  │   │
│  │  . . . . . . . .  │  │  Confidence:    │   │
│  │  ♙ ♙ ♙ ♙ ♙ ♙ ♙ ♙  │  │  Average: 85%  │   │
│  │  ♖ ♘ ♗ ♕ ♔ ♗ ♘ ♖  │  │  Range: 65-98% │   │
│  │                  │  │                  │   │
│  │  (with confidence│  │  Low Conf:      │   │
│  │   indicators)    │  │  • e4: P (68%)  │   │
│  └──────────────────┘  └──────────────────┘   │
└────────────────────────────────────────────────┘
```

### EngineAnalysisWidget
```
┌─────────────────────────────────────────────────────────┐
│            Engine Analysis Widget (Tabbed)              │
├─────────────────────────────────────────────────────────┤
│  ┌─────────┬────────────┬──────────────┐               │
│  │Threat   │Best Moves  │Analysis Text │               │
│  │  Map    │            │              │               │
│  └─┬───────┴────────────┴──────────────┘               │
│    │                                                    │
│  ┌─▼───────────────────────────────────────────────┐   │
│  │  Threat Map Tab:                                │   │
│  │  ┌───────────────────────────────────────────┐  │   │
│  │  │  Board with Color-Coded Squares:          │  │   │
│  │  │  • Light Red: White attacks              │  │   │
│  │  │  • Dark Red: Black attacks               │  │   │
│  │  │  • Purple: Both attack                   │  │   │
│  │  │  • Red Circles: Hanging pieces           │  │   │
│  │  └───────────────────────────────────────────┘  │   │
│  │                                                  │   │
│  │  Best Moves Tab:                                │   │
│  │  ┌───────────────────────────────────────────┐  │   │
│  │  │  Board with Move Arrows:                  │  │   │
│  │  │  • Green Arrow (1): Best move             │  │   │
│  │  │  • Blue Arrow (2): Second best            │  │   │
│  │  │  • Yellow Arrow (3): Third                │  │   │
│  │  │  • Orange Arrow (4): Fourth               │  │   │
│  │  │  • Purple Arrow (5): Fifth                │  │   │
│  │  │  • Numbered labels on destinations        │  │   │
│  │  └───────────────────────────────────────────┘  │   │
│  │                                                  │   │
│  │  Analysis Text Tab:                             │   │
│  │  • Threat analysis summary                      │   │
│  │  • Move explanations with scores                │   │
│  │  • Tactical themes                              │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

## File Organization

```
chess-engine/
│
├── run_pyside6.py ──────────────── Entry point
│
├── src/
│   └── gui_pyside6/ ─────────────── GUI package
│       ├── __init__.py
│       ├── main_window.py ──────── Main application (494 lines)
│       └── widgets/ ─────────────── Widget subpackage
│           ├── __init__.py
│           ├── control_panel.py ── Control buttons (208 lines)
│           ├── pipeline_widget.py  Pipeline viz (456 lines)
│           ├── board_widget.py ─── Board display (344 lines)
│           └── analysis_widget.py  Engine viz (430 lines)
│
├── tests/
│   └── gui_pyside6/ ─────────────── Tests
│       ├── __init__.py
│       └── test_widgets.py ──────── Widget tests (97 lines)
│
├── examples/
│   └── pyside6_gui_example.py ──── Demo script (84 lines)
│
└── docs/
    ├── PYSIDE6_GUI_README.md ───── User guide (414 lines)
    ├── PYSIDE6_IMPLEMENTATION_
    │   SUMMARY.md ──────────────── Tech summary (416 lines)
    └── PYSIDE6_ARCHITECTURE.md ─── This file

Total: ~2,943 lines of code and documentation
```

## Color Coding Guide

### Threat Map Colors
- **Light Red** (255, 100, 100, 100): Squares attacked by White
- **Dark Red** (139, 0, 0, 100): Squares attacked by Black
- **Purple** (128, 0, 128, 100): Squares attacked by both
- **Red Circle** (255, 0, 0): Hanging piece indicator

### Move Arrow Colors
- **Green** (0, 200, 0, 200): Best move (#1)
- **Blue** (100, 150, 255, 180): Second best (#2)
- **Yellow** (255, 200, 0, 160): Third best (#3)
- **Orange** (255, 150, 100, 140): Fourth best (#4)
- **Purple** (200, 100, 200, 120): Fifth best (#5)

### Confidence Colors
- **Green**: High confidence (>80%)
- **Orange**: Medium confidence (50-80%)
- **Red**: Low confidence (<50%)

### Board Colors
- **Light Squares**: (240, 217, 181)
- **Dark Squares**: (181, 136, 99)

---

*This architecture provides a solid foundation for a professional chess engine GUI application with excellent separation of concerns, maintainability, and user experience.*
