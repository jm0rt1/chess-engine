"""
Widgets Module for PySide6 Chess Engine GUI.

This module contains custom widgets for various GUI components.
"""

from .control_panel import ControlPanelWidget
from .pipeline_widget import PipelineVisualizationWidget
from .board_widget import BoardReconstructionWidget
from .analysis_widget import EngineAnalysisWidget

__all__ = [
    'ControlPanelWidget',
    'PipelineVisualizationWidget',
    'BoardReconstructionWidget',
    'EngineAnalysisWidget',
]
