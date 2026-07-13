from PyQt6.QtGui import QColor, QPalette


class Nord:
    bg_0 = "#1d232f"
    bg_1 = "#252c3a"
    bg_2 = "#2d3546"

    border = "#3d465b"
    border_light = "#48526b"

    fg_0 = "#d8dee9"
    fg_1 = "#bfc9db"
    fg_2 = "#8f9db3"
    fg_3 = "#6a7b96"

    accent = "#5e81ac"
    accent_light = "#81a1c1"
    accent_dark = "#4c6a8d"

    success = "#88c0d0"
    warning = "#ebcb8b"
    error = "#bf616a"

    tool_bg = "#2d3546"
    user_bg = "#253544"
    user_border = "#3a5a7a"

    ui_font = "Inter"
    mono_font = "JetBrains Mono"


def make_palette() -> QPalette:
    p = QPalette()
    p.setColor(QPalette.ColorRole.Window, QColor(Nord.bg_0))
    p.setColor(QPalette.ColorRole.WindowText, QColor(Nord.fg_0))
    p.setColor(QPalette.ColorRole.Base, QColor(Nord.bg_1))
    p.setColor(QPalette.ColorRole.AlternateBase, QColor(Nord.bg_0))
    p.setColor(QPalette.ColorRole.ToolTipBase, QColor(Nord.bg_2))
    p.setColor(QPalette.ColorRole.ToolTipText, QColor(Nord.fg_0))
    p.setColor(QPalette.ColorRole.Text, QColor(Nord.fg_0))
    p.setColor(QPalette.ColorRole.Button, QColor(Nord.bg_2))
    p.setColor(QPalette.ColorRole.ButtonText, QColor(Nord.fg_0))
    p.setColor(QPalette.ColorRole.BrightText, QColor(Nord.error))
    p.setColor(QPalette.ColorRole.Link, QColor(Nord.accent))
    p.setColor(QPalette.ColorRole.Highlight, QColor(Nord.accent))
    p.setColor(QPalette.ColorRole.HighlightedText, QColor(Nord.fg_0))
    return p
