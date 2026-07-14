from __future__ import annotations

import os

from PyQt6.QtCore import QSettings, Qt, QSize, pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSlider,
    QSpinBox,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from ..theme.palette import Dark
from ..theme.typography import Font


MAX_CPUS = os.cpu_count() or 4


class SettingsDialog(QDialog):
    """Settings dialog with QSettings persistence.

    Flat, monospace, no rounded corners. Developer aesthetic.
    """

    settings_changed = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._settings = QSettings("DAN", "DAN")
        self.setWindowTitle("Settings")
        self.setMinimumSize(700, 500)
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.setStyleSheet(
            f"""
            QDialog {{ background: {Dark.bg_0}; }}
            QListWidget {{
                background: {Dark.bg_1};
                border: none;
                border-right: 1px solid {Dark.border};
                outline: none;
                padding: 4px;
            }}
            QListWidget::item {{
                color: {Dark.fg_2};
                padding: 8px 16px;
                margin: 1px 4px;
            }}
            QListWidget::item:selected {{
                color: {Dark.fg_0};
                background: {Dark.bg_2};
            }}
            QListWidget::item:hover {{
                color: {Dark.fg_1};
                background: {Dark.bg_2};
            }}
            QGroupBox {{
                color: {Dark.fg_1};
                border: 1px solid {Dark.border};
                margin-top: 12px;
                padding-top: 16px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 6px;
            }}
            QLabel {{ color: {Dark.fg_0}; background: transparent; }}
            QComboBox {{
                background: {Dark.bg_2}; color: {Dark.fg_0};
                border: 1px solid {Dark.border};
                padding: 6px 12px; min-width: 160px;
            }}
            QComboBox:hover {{ border-color: {Dark.accent}; }}
            QComboBox::drop-down {{ border: none; width: 24px; }}
            QComboBox QAbstractItemView {{
                background: {Dark.bg_2}; color: {Dark.fg_0};
                border: 1px solid {Dark.border};
                selection-background-color: {Dark.accent};
            }}
            QLineEdit {{
                background: {Dark.bg_2}; color: {Dark.fg_0};
                border: 1px solid {Dark.border};
                padding: 6px 12px;
            }}
            QLineEdit:focus {{ border-color: {Dark.accent}; }}
            QSpinBox {{
                background: {Dark.bg_2}; color: {Dark.fg_0};
                border: 1px solid {Dark.border};
                padding: 6px 12px;
            }}
            QSlider::groove:horizontal {{
                background: {Dark.border}; height: 4px;
            }}
            QSlider::handle:horizontal {{
                background: {Dark.accent}; width: 12px; height: 12px;
                margin: -4px 0;
            }}
            QSlider::handle:horizontal:hover {{ background: {Dark.accent_light}; }}
            QPushButton {{
                background: {Dark.bg_2}; color: {Dark.fg_0};
                border: 1px solid {Dark.border};
                padding: 8px 20px;
            }}
            QPushButton:hover {{ border-color: {Dark.accent}; }}
            QPushButton:pressed {{ background: {Dark.accent}; color: {Dark.bg_0}; }}
        """
        )

        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._nav = QListWidget()
        self._nav.setFont(Font.mono(11))
        self._nav.setFixedWidth(180)
        self._nav.setIconSize(QSize(16, 16))
        root.addWidget(self._nav)

        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(24, 24, 24, 24)

        self._stack = QStackedWidget()
        right_layout.addWidget(self._stack, 1)

        btn_row = QHBoxLayout()
        btn_row.addStretch()

        save_btn = QPushButton("Save")
        save_btn.setFont(Font.mono(11))
        save_btn.clicked.connect(self._save_and_accept)
        btn_row.addWidget(save_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFont(Font.mono(11))
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)

        right_layout.addLayout(btn_row)

        root.addWidget(right, 1)

        self._pages: list[tuple[str, QWidget]] = []
        self._add_pages()

        self._nav.currentRowChanged.connect(self._stack.setCurrentIndex)
        self._nav.setCurrentRow(0)

    def _add_pages(self) -> None:
        self._add_page("General", self._general_page())
        self._add_page("Appearance", self._appearance_page())
        self._add_page("AI", self._ai_page())
        self._add_page("Models", self._models_page())
        self._add_page("Performance", self._performance_page())
        self._add_page("Plugins", self._plugins_page())
        self._add_page("Developer", self._developer_page())
        self._add_page("Advanced", self._advanced_page())

    def _add_page(self, name: str, widget: QWidget) -> None:
        item = QListWidgetItem(name)
        item.setSizeHint(QSize(0, 32))
        self._nav.addItem(item)
        self._stack.addWidget(widget)
        self._pages.append((name, widget))

    def _save_and_accept(self) -> None:
        self._sync_combo("auto_connect", "auto_connect")
        self._sync_line("default_command", "default_command")
        self._sync_combo("confirm_dangerous", "confirm_dangerous")
        self._sync_combo("theme_mode", "theme_mode")
        self._sync_line("accent_color", "accent_color")
        self._sync_spin("corner_radius", "corner_radius")
        self._sync_line("mono_font", "mono_font")
        self._sync_slider("ui_scale", "ui_scale")
        self._sync_combo("compact_mode", "compact_mode")
        self._sync_combo("animations", "animations")
        self._sync_line("default_model", "default_model")
        self._sync_slider("temperature", "temperature")
        self._sync_spin("max_tokens", "max_tokens")
        self._sync_spin("context_size", "context_size")
        self._sync_combo("streaming", "streaming")
        self._sync_spin("worker_threads", "worker_threads")
        self._sync_spin("request_timeout", "request_timeout")
        self._sync_line("custom_prompt", "custom_prompt")
        self._sync_line("model_interpret", "model_interpret")
        self._sync_line("model_reason", "model_reason")
        self._sync_line("model_persona", "model_persona")
        self._sync_line("endpoint", "endpoint")
        self._sync_combo("debug_logs", "debug_logs")
        self._sync_combo("api_diagnostics", "api_diagnostics")
        self._sync_combo("experimental", "experimental")
        self.settings_changed.emit()
        self.accept()

    def _sync_combo(self, combo_name: str, key: str) -> None:
        combo = getattr(self, combo_name, None)
        if combo:
            self._settings.setValue(key, combo.currentText())

    def _sync_line(self, line_name: str, key: str) -> None:
        line = getattr(self, line_name, None)
        if line:
            self._settings.setValue(key, line.text())

    def _sync_spin(self, spin_name: str, key: str) -> None:
        spin = getattr(self, spin_name, None)
        if spin:
            self._settings.setValue(key, spin.value())

    def _sync_slider(self, slider_name: str, key: str) -> None:
        slider = getattr(self, slider_name, None)
        if slider:
            self._settings.setValue(key, slider.value())

    def _combo(self, items: list[str], key: str) -> QComboBox:
        cb = QComboBox()
        cb.setFont(Font.mono(11))
        cb.addItems(items)
        saved = self._settings.value(key, "")
        if saved:
            idx = cb.findText(saved)
            if idx >= 0:
                cb.setCurrentIndex(idx)
        return cb

    def _line(self, default: str, key: str) -> QLineEdit:
        le = QLineEdit(self._settings.value(key, default))
        le.setFont(Font.mono(11))
        return le

    def _spin(self, default: int, lo: int, hi: int, key: str) -> QSpinBox:
        sb = QSpinBox()
        sb.setFont(Font.mono(11))
        sb.setRange(lo, hi)
        val = int(self._settings.value(key, default))
        sb.setValue(max(lo, min(hi, val)))
        return sb

    def _slider(self, default: int, lo: int, hi: int, key: str) -> QSlider:
        sl = QSlider(Qt.Orientation.Horizontal)
        sl.setRange(lo, hi)
        val = int(self._settings.value(key, default))
        sl.setValue(max(lo, min(hi, val)))
        return sl

    def _general_page(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(16)

        grp = QGroupBox("Startup")
        grp.setFont(Font.mono(10))
        form = QFormLayout(grp)
        self.auto_connect = self._combo(["Yes", "No"], "auto_connect")
        form.addRow("Auto-connect:", self.auto_connect)
        self.default_command = self._line("Hello", "default_command")
        form.addRow("Default command:", self.default_command)
        layout.addWidget(grp)

        grp2 = QGroupBox("Behavior")
        grp2.setFont(Font.mono(10))
        form2 = QFormLayout(grp2)
        self.confirm_dangerous = self._combo(["Always", "Never"], "confirm_dangerous")
        form2.addRow("Confirm dangerous:", self.confirm_dangerous)
        layout.addWidget(grp2)

        layout.addStretch()
        return w

    def _appearance_page(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(16)

        grp = QGroupBox("Theme")
        grp.setFont(Font.mono(10))
        form = QFormLayout(grp)
        self.theme_mode = self._combo(["Dark", "Light", "System"], "theme_mode")
        form.addRow("Mode:", self.theme_mode)
        self.accent_color = self._line(Dark.accent, "accent_color")
        form.addRow("Accent color:", self.accent_color)
        self.corner_radius = self._spin(0, 0, 20, "corner_radius")
        form.addRow("Corner radius:", self.corner_radius)
        layout.addWidget(grp)

        grp2 = QGroupBox("Typography")
        grp2.setFont(Font.mono(10))
        form2 = QFormLayout(grp2)
        self.mono_font = self._line("JetBrains Mono", "mono_font")
        form2.addRow("Mono font:", self.mono_font)
        self.ui_scale = self._slider(100, 50, 200, "ui_scale")
        form2.addRow("UI scale:", self.ui_scale)
        layout.addWidget(grp2)

        grp3 = QGroupBox("Behavior")
        grp3.setFont(Font.mono(10))
        form3 = QFormLayout(grp3)
        self.compact_mode = self._combo(["Off", "On"], "compact_mode")
        form3.addRow("Compact mode:", self.compact_mode)
        self.animations = self._combo(["On", "Off"], "animations")
        form3.addRow("Animations:", self.animations)
        layout.addWidget(grp3)

        layout.addStretch()
        return w

    def _ai_page(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(16)

        grp = QGroupBox("Model")
        grp.setFont(Font.mono(10))
        form = QFormLayout(grp)
        self.default_model = self._line("dan-persona", "default_model")
        form.addRow("Default model:", self.default_model)
        temperature = self._slider(70, 0, 100, "temperature")
        self.temperature = temperature
        form.addRow("Temperature:", temperature)
        self.max_tokens = self._spin(256, 64, 4096, "max_tokens")
        form.addRow("Max tokens:", self.max_tokens)
        self.context_size = self._spin(20, 5, 100, "context_size")
        form.addRow("Context size:", self.context_size)
        layout.addWidget(grp)

        grp2 = QGroupBox("Streaming")
        grp2.setFont(Font.mono(10))
        form2 = QFormLayout(grp2)
        self.streaming = self._combo(["Yes", "No"], "streaming")
        form2.addRow("Enable streaming:", self.streaming)
        layout.addWidget(grp2)

        grp3 = QGroupBox("System prompt")
        grp3.setFont(Font.mono(10))
        form3 = QFormLayout(grp3)
        self.custom_prompt = self._line("", "custom_prompt")
        form3.addRow("Custom prompt:", self.custom_prompt)
        layout.addWidget(grp3)

        layout.addStretch()
        return w

    def _models_page(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(16)

        grp = QGroupBox("Models")
        grp.setFont(Font.mono(10))
        form = QFormLayout(grp)
        self.model_interpret = self._line("dan-interp", "model_interpret")
        form.addRow("Interpret:", self.model_interpret)
        self.model_reason = self._line("dan-reason", "model_reason")
        form.addRow("Reason:", self.model_reason)
        self.model_persona = self._line("dan-persona", "model_persona")
        form.addRow("Persona:", self.model_persona)
        self.endpoint = self._line("http://localhost:11434", "endpoint")
        form.addRow("Endpoint:", self.endpoint)
        layout.addWidget(grp)

        layout.addStretch()
        return w

    def _performance_page(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(16)

        grp = QGroupBox("Performance")
        grp.setFont(Font.mono(10))
        form = QFormLayout(grp)
        self.worker_threads = self._spin(MAX_CPUS, 1, MAX_CPUS, "worker_threads")
        form.addRow("Worker threads:", self.worker_threads)
        self.request_timeout = self._spin(300, 10, 600, "request_timeout")
        form.addRow("Request timeout:", self.request_timeout)
        layout.addWidget(grp)

        layout.addStretch()
        return w

    def _plugins_page(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(16)
        lbl = QLabel("No plugins configured.")
        lbl.setFont(Font.mono(12))
        lbl.setStyleSheet(f"color: {Dark.fg_3};")
        layout.addWidget(lbl)
        layout.addStretch()
        return w

    def _developer_page(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(16)

        grp = QGroupBox("Debug")
        grp.setFont(Font.mono(10))
        form = QFormLayout(grp)
        self.debug_logs = self._combo(["Off", "On"], "debug_logs")
        form.addRow("Debug logs:", self.debug_logs)
        self.api_diagnostics = self._combo(["Off", "On"], "api_diagnostics")
        form.addRow("API diagnostics:", self.api_diagnostics)
        layout.addWidget(grp)

        grp2 = QGroupBox("Experimental")
        grp2.setFont(Font.mono(10))
        form2 = QFormLayout(grp2)
        self.experimental = self._combo(["Off", "On"], "experimental")
        form2.addRow("Features:", self.experimental)
        layout.addWidget(grp2)

        layout.addStretch()
        return w

    def _advanced_page(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(16)
        lbl = QLabel("Advanced settings for power users.")
        lbl.setFont(Font.mono(12))
        lbl.setStyleSheet(f"color: {Dark.fg_3};")
        layout.addWidget(lbl)
        layout.addStretch()
        return w
