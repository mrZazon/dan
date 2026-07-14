from __future__ import annotations

from PyQt6.QtCore import (
    QEasingCurve,
    QPropertyAnimation,
    pyqtProperty,
)
from PyQt6.QtGui import QColor, QPainter
from PyQt6.QtWidgets import QWidget


class BreathingDot(QWidget):
    """A minimal opacity-pulsing dot indicator.

    Subtle, fast, no size animation. Just a calm opacity pulse.
    """

    def __init__(self, parent: QWidget | None = None, color: str = "#7289c8") -> None:
        super().__init__(parent)
        self._color = QColor(color)
        self._opacity = 0.4

        self._anim = QPropertyAnimation(self, b"dotOpacity")
        self._anim.setDuration(800)
        self._anim.setStartValue(0.3)
        self._anim.setKeyValueAt(0.5, 0.9)
        self._anim.setEndValue(0.3)
        self._anim.setEasingCurve(QEasingCurve.Type.InOutSine)
        self._anim.setLoopCount(-1)

    @pyqtProperty(float)
    def dotOpacity(self) -> float:
        return self._opacity

    @dotOpacity.setter
    def dotOpacity(self, val: float) -> None:
        self._opacity = val
        self.update()

    def set_color(self, color: str) -> None:
        self._color = QColor(color)
        self.update()

    def start(self) -> None:
        self._anim.start()

    def stop(self) -> None:
        self._anim.stop()
        self._opacity = 0.0
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        if self._opacity <= 0.01:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setOpacity(self._opacity)
        painter.setBrush(self._color)
        painter.setPen(self._color)
        size = 6
        x = (self.width() - size) // 2
        y = (self.height() - size) // 2
        painter.drawEllipse(x, y, size, size)
        painter.end()
