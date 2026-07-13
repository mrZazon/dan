from __future__ import annotations

import asyncio
import logging
import os
import sys
from pathlib import Path

from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtWidgets import QApplication

from dan.core.config import DANConfig

from .window import MainWindow

logger = logging.getLogger("dan.gui")

APPLE_BG = "#1c1c1e"
APPLE_BG2 = "#2c2c2e"
APPLE_SURFACE = "#3a3a3c"
APPLE_SEPARATOR = "#48484a"
APPLE_LABEL = "#ebebf5"
APPLE_SECONDARY = "#98989e"
APPLE_TERTIARY = "#636366"
APPLE_ACCENT = "#64d2ff"
APPLE_ACCENT_HOVER = "#8ae1ff"
APPLE_RED = "#ff453a"
APPLE_GREEN = "#30d158"
APPLE_YELLOW = "#ffd60a"


def setup_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(level=level, format="%(name)s %(message)s", datefmt="%H:%M:%S")
    if not verbose:
        for name in ("httpx", "httpcore", "urllib3"):
            logging.getLogger(name).setLevel(logging.CRITICAL)


def main() -> None:
    setup_logging(False)

    app = QApplication(sys.argv)
    app.setApplicationName("D.A.N.")
    app.setOrganizationName("dan")
    app.setApplicationVersion("0.1.0")

    font = QFont("SF Pro Display", 10)
    app.setFont(font)

    app.setStyle("Fusion")
    app.setPalette(_apple_palette())
    app.setStyleSheet(_apple_stylesheet())

    icon_path = _pick_icon()
    icon = QIcon(icon_path)
    app.setWindowIcon(icon)

    config = DANConfig.from_file()
    config.ensure_dirs()

    window = MainWindow(config)
    window.setWindowIcon(icon)
    window.show()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    timer = QTimer()
    timer.timeout.connect(lambda: (loop.call_soon(loop.stop), loop.run_forever()))
    timer.start(50)

    # Connect to API server once the event loop is ready
    loop.call_soon(lambda: window.connect_to_server(loop))

    sys.exit(app.exec())


def _is_dark_desktop() -> bool:
    kde_cfg = Path.home() / ".config" / "kdeglobals"
    if kde_cfg.exists():
        try:
            text = kde_cfg.read_text()
            if "ColorScheme=Konsole" in text or "ColorScheme=BreezeDark" in text:
                return True
            if "ColorScheme=BreezeLight" in text or "ColorScheme=Breeze" in text:
                return False
        except Exception:
            pass
    for var in ("GTK_THEME",):
        raw = os.environ.get(var, "").lower()
        if "dark" in raw:
            return True
        if "light" in raw:
            return False
    return True


def _pick_icon() -> str:
    base = Path(__file__).resolve().parent.parent.parent / "icon"
    dark_icon = str(base / "icon-dark.png")
    light_icon = str(base / "icon-light.png")
    if not Path(dark_icon).exists() or not Path(light_icon).exists():
        if Path(dark_icon).exists():
            return dark_icon
        if Path(light_icon).exists():
            return light_icon
        return ""
    return dark_icon if _is_dark_desktop() else light_icon


def _apple_palette():
    from PyQt6.QtGui import QColor, QPalette
    p = QPalette()
    p.setColor(QPalette.ColorRole.Window, QColor(APPLE_BG))
    p.setColor(QPalette.ColorRole.WindowText, QColor(APPLE_LABEL))
    p.setColor(QPalette.ColorRole.Base, QColor(APPLE_BG2))
    p.setColor(QPalette.ColorRole.AlternateBase, QColor(APPLE_BG))
    p.setColor(QPalette.ColorRole.ToolTipBase, QColor(APPLE_BG2))
    p.setColor(QPalette.ColorRole.ToolTipText, QColor(APPLE_LABEL))
    p.setColor(QPalette.ColorRole.Text, QColor(APPLE_LABEL))
    p.setColor(QPalette.ColorRole.Button, QColor(APPLE_SURFACE))
    p.setColor(QPalette.ColorRole.ButtonText, QColor(APPLE_LABEL))
    p.setColor(QPalette.ColorRole.BrightText, QColor(APPLE_RED))
    p.setColor(QPalette.ColorRole.Link, QColor(APPLE_ACCENT))
    p.setColor(QPalette.ColorRole.Highlight, QColor(0, 120, 215))
    p.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
    return p


def _apple_stylesheet() -> str:
    return f"""
    QMainWindow {{
        background-color: {APPLE_BG};
    }}
    QToolTip {{
        background-color: {APPLE_BG2};
        color: {APPLE_LABEL};
        border: 1px solid {APPLE_SEPARATOR};
        border-radius: 6px;
        padding: 6px 10px;
        font-size: 12px;
    }}
    QScrollBar:vertical {{
        background: transparent;
        width: 8px;
        margin: 0;
    }}
    QScrollBar::handle:vertical {{
        background: {APPLE_TERTIARY};
        min-height: 30px;
        border-radius: 4px;
        margin: 2px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {APPLE_SECONDARY};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    QScrollBar:horizontal {{
        height: 0px;
    }}
    QStatusBar {{
        background: {APPLE_BG};
        border-top: 1px solid {APPLE_SEPARATOR};
        color: {APPLE_SECONDARY};
        font-size: 11px;
        padding: 2px 10px;
    }}
    QStatusBar::item {{
        border: none;
    }}
    QMenuBar {{
        background-color: {APPLE_BG};
        border: none;
        padding: 2px 0;
    }}
    QMenuBar::item {{
        color: {APPLE_LABEL};
        padding: 4px 12px;
        border-radius: 4px;
    }}
    QMenuBar::item:selected {{
        background: {APPLE_SURFACE};
    }}
    QMenu {{
        background-color: {APPLE_BG2};
        border: 1px solid {APPLE_SEPARATOR};
        border-radius: 8px;
        padding: 6px;
    }}
    QMenu::item {{
        color: {APPLE_LABEL};
        padding: 6px 20px;
        border-radius: 4px;
    }}
    QMenu::item:selected {{
        background: {APPLE_ACCENT};
        color: {APPLE_BG};
    }}
    QMenu::separator {{
        height: 1px;
        background: {APPLE_SEPARATOR};
        margin: 4px 10px;
    }}
    QGroupBox {{
        border: 1px solid {APPLE_SEPARATOR};
        border-radius: 10px;
        margin-top: 16px;
        padding-top: 12px;
        font-weight: 500;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 14px;
        padding: 0 8px;
        color: {APPLE_SECONDARY};
    }}
    QLineEdit {{
        background-color: {APPLE_BG2};
        border: 1px solid {APPLE_SEPARATOR};
        border-radius: 8px;
        padding: 8px 14px;
        color: {APPLE_LABEL};
        font-size: 13px;
        selection-background-color: {APPLE_ACCENT};
        selection-color: {APPLE_BG};
    }}
    QLineEdit:focus {{
        border-color: {APPLE_ACCENT};
    }}
    QLineEdit::placeholder {{
        color: {APPLE_TERTIARY};
    }}
    QPushButton {{
        background-color: {APPLE_ACCENT};
        color: {APPLE_BG};
        border: none;
        border-radius: 8px;
        padding: 8px 20px;
        font-weight: 600;
        font-size: 13px;
    }}
    QPushButton:hover {{
        background-color: {APPLE_ACCENT_HOVER};
    }}
    QPushButton:pressed {{
        background-color: #4aa8d4;
    }}
    QPushButton:disabled {{
        background-color: {APPLE_SURFACE};
        color: {APPLE_TERTIARY};
    }}
    QTableWidget {{
        background: transparent;
        border: none;
        font-size: 12px;
        outline: none;
    }}
    QTableWidget::item {{
        color: {APPLE_LABEL};
        padding: 6px 8px;
        border-bottom: 1px solid rgba(72, 72, 74, 30);
    }}
    QTableWidget::item:selected {{
        background: rgba(100, 210, 255, 25);
        color: {APPLE_LABEL};
    }}
    QHeaderView::section {{
        background: transparent;
        color: {APPLE_SECONDARY};
        border: none;
        border-bottom: 1px solid {APPLE_SEPARATOR};
        padding: 8px;
        font-weight: 600;
        font-size: 11px;
    }}
    QTreeWidget {{
        background: transparent;
        border: none;
        font-size: 12px;
        outline: none;
    }}
    QTreeWidget::item {{
        color: {APPLE_LABEL};
        padding: 6px 12px;
        border: none;
    }}
    QTreeWidget::item:hover {{
        background: rgba(255, 255, 255, 5);
    }}
    QTreeWidget::item:selected {{
        background: rgba(100, 210, 255, 25);
        color: {APPLE_LABEL};
    }}
    QComboBox {{
        background-color: {APPLE_BG2};
        border: 1px solid {APPLE_SEPARATOR};
        border-radius: 8px;
        padding: 8px 14px;
        color: {APPLE_LABEL};
        font-size: 13px;
    }}
    QComboBox:focus {{
        border-color: {APPLE_ACCENT};
    }}
    QComboBox::drop-down {{
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 24px;
        border: none;
    }}
    QComboBox QAbstractItemView {{
        background-color: {APPLE_BG2};
        border: 1px solid {APPLE_SEPARATOR};
        border-radius: 8px;
        selection-background-color: rgba(100, 210, 255, 25);
        selection-color: {APPLE_LABEL};
        padding: 4px;
    }}
    QDoubleSpinBox, QSpinBox {{
        background-color: {APPLE_BG2};
        border: 1px solid {APPLE_SEPARATOR};
        border-radius: 8px;
        padding: 6px 10px;
        color: {APPLE_LABEL};
        font-size: 13px;
    }}
    QDoubleSpinBox:focus, QSpinBox:focus {{
        border-color: {APPLE_ACCENT};
    }}
    QScrollArea {{
        background: transparent;
    }}
    QSplitter::handle {{
        background: {APPLE_SEPARATOR};
        width: 1px;
    }}
    QDialog {{
        background: {APPLE_BG};
    }}
    QDialogButtonBox QPushButton {{
        min-width: 80px;
    }}
    """
