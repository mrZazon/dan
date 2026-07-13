from __future__ import annotations

from typing import TYPE_CHECKING, Any

from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QLineEdit,
    QSpinBox,
    QVBoxLayout,
)

if TYPE_CHECKING:
    from dan.core.config import DANConfig


FIELD_STYLE = """
    QLabel {
        color: #98989e;
        font-size: 12px;
        font-weight: 500;
    }
"""


class ConfigDialog(QDialog):
    def __init__(self, config: DANConfig, parent: Any = None) -> None:
        super().__init__(parent)
        self._config = config
        self._result: DANConfig | None = None

        self.setWindowTitle("D.A.N. Configuration")
        self.setMinimumWidth(540)
        self.setStyleSheet("""
            QDialog {
                background: #1c1c1e;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)

        self._build_core(layout, config)
        self._build_models(layout, config)
        self._build_memory(layout, config)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _build_core(self, layout: QVBoxLayout, config: DANConfig) -> None:
        g = QGroupBox("Core")
        form = QFormLayout(g)
        form.setSpacing(10)

        self._threshold = QDoubleSpinBox()
        self._threshold.setRange(0.0, 2.0)
        self._threshold.setSingleStep(0.1)
        self._threshold.setValue(config.core.threshold)
        self._threshold.setFixedWidth(120)
        form.addRow("Threshold:", self._threshold)

        self._log_level = QComboBox()
        self._log_level.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        self._log_level.setCurrentText(config.core.log_level)
        self._log_level.setFixedWidth(140)
        form.addRow("Log Level:", self._log_level)

        layout.addWidget(g)

    def _build_models(self, layout: QVBoxLayout, config: DANConfig) -> None:
        self._interpret_model = QLineEdit(config.interpret.model)
        self._interpret_model.setPlaceholderText("qwen3.5:2b")
        self._reason_model = QLineEdit(config.reason.model)
        self._reason_model.setPlaceholderText("qwen3.5:2b")
        self._persona_model = QLineEdit(config.persona.model)
        self._persona_model.setPlaceholderText("qwen3.5:2b")
        self._interpret_quant = QLineEdit(config.interpret.quantization)
        self._interpret_quant.setPlaceholderText("nf4")
        self._reason_quant = QLineEdit(config.reason.quantization)
        self._reason_quant.setPlaceholderText("nf4")
        self._persona_quant = QLineEdit(config.persona.quantization)
        self._persona_quant.setPlaceholderText("nf4")

        for title, model_input, quant_input in [
            ("Interpret Model (L1)", self._interpret_model, self._interpret_quant),
            ("Reason Model (L2)", self._reason_model, self._reason_quant),
            ("Persona Model (L3)", self._persona_model, self._persona_quant),
        ]:
            g = QGroupBox(title)
            form = QFormLayout(g)
            form.setSpacing(10)
            form.addRow("Model:", model_input)
            form.addRow("Quantization:", quant_input)
            layout.addWidget(g)

    def _build_memory(self, layout: QVBoxLayout, config: DANConfig) -> None:
        g = QGroupBox("Memory")
        form = QFormLayout(g)
        form.setSpacing(10)

        self._short_term = QSpinBox()
        self._short_term.setRange(10, 500)
        self._short_term.setValue(config.memory.short_term_limit)
        self._short_term.setSuffix(" turns")
        self._short_term.setFixedWidth(140)
        form.addRow("Short-term limit:", self._short_term)

        self._long_term = QLineEdit(config.memory.long_term_path)
        form.addRow("Long-term path:", self._long_term)

        layout.addWidget(g)

    def _accept(self) -> None:
        from dan.core.config import CoreConfig, MemoryConfig, ProviderConfig

        self._config.core = CoreConfig(
            threshold=self._threshold.value(),
            log_level=self._log_level.currentText(),
        )
        self._config.interpret = ProviderConfig(
            name="ollama",
            model=self._interpret_model.text(),
            quantization=self._interpret_quant.text(),
        )
        self._config.reason = ProviderConfig(
            name="ollama",
            model=self._reason_model.text(),
            quantization=self._reason_quant.text(),
        )
        self._config.persona = ProviderConfig(
            name="ollama",
            model=self._persona_model.text(),
            quantization=self._persona_quant.text(),
        )
        self._config.memory = MemoryConfig(
            short_term_limit=self._short_term.value(),
            long_term_path=self._long_term.text(),
        )
        self._result = self._config
        self.accept()

    @property
    def result(self) -> DANConfig | None:
        return self._result
