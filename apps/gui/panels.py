from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QHeaderView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from dan.core.tool_registry import ToolRegistry
    from dan.plugins.registry import PluginRegistry
    from dan.skills.registry import SkillRegistry


HEADER_STYLE = """
    QLabel {
        color: #98989e;
        font-weight: 600;
        font-size: 11px;
        letter-spacing: 0.5px;
        padding: 20px 16px 4px;
        background: transparent;
    }
"""

COUNT_STYLE = """
    QLabel {
        color: #636366;
        font-size: 11px;
        padding: 0 16px 12px;
        background: transparent;
    }
"""


class ToolPanel(QWidget):
    def __init__(self, registry: ToolRegistry, parent: QWidget = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(QLabel("TOOLS", styleSheet=HEADER_STYLE))

        cl = QLabel(f"{len(registry.tools())} registered", styleSheet=COUNT_STYLE)
        layout.addWidget(cl)

        self._tree = QTreeWidget()
        self._tree.setHeaderHidden(True)
        self._tree.setRootIsDecorated(False)
        self._tree.setIndentation(8)
        self._tree.setStyleSheet("""
            QTreeWidget {
                background: transparent;
                border: none;
                font-size: 12px;
            }
            QTreeWidget::item {
                color: #ebebf5;
                padding: 5px 16px;
                border: none;
            }
            QTreeWidget::item:hover {
                background: rgba(255, 255, 255, 5);
            }
            QTreeWidget::item:selected {
                background: rgba(100, 210, 255, 20);
                color: #ebebf5;
            }
        """)
        layout.addWidget(self._tree)

        for tool_cls in registry.tools():
            inst = tool_cls()
            item = QTreeWidgetItem([inst.name])
            item.setToolTip(0, inst.description)
            self._tree.addTopLevelItem(item)

        self._tree.sortItems(0, Qt.SortOrder.AscendingOrder)


class SkillPanel(QWidget):
    def __init__(self, registry: SkillRegistry, parent: QWidget = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(QLabel("SKILLS", styleSheet=HEADER_STYLE))

        cl = QLabel(f"{len(registry.list_skills())} learned", styleSheet=COUNT_STYLE)
        layout.addWidget(cl)

        self._table = QTableWidget()
        self._table.setColumnCount(4)
        self._table.setHorizontalHeaderLabels(["Name", "Tool", "Intent", "Rate"])
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setShowGrid(False)
        self._table.verticalHeader().setVisible(False)
        self._table.setStyleSheet("""
            QTableWidget {
                background: transparent;
                border: none;
                font-size: 12px;
            }
            QTableWidget::item {
                color: #ebebf5;
                padding: 5px 8px;
                border: none;
            }
            QTableWidget::item:selected {
                background: rgba(100, 210, 255, 20);
            }
        """)
        layout.addWidget(self._table)

        skills = registry.list_skills()
        self._table.setRowCount(len(skills))
        for i, skill in enumerate(skills):
            self._table.setItem(i, 0, QTableWidgetItem(skill.name))
            self._table.setItem(i, 1, QTableWidgetItem(skill.tool_name))
            self._table.setItem(i, 2, QTableWidgetItem(skill.intent))
            rate_item = QTableWidgetItem(f"{skill.success_rate:.0%}")
            rate_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._table.setItem(i, 3, rate_item)


class PluginPanel(QWidget):
    def __init__(self, registry: PluginRegistry, parent: QWidget = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(QLabel("PLUGINS", styleSheet=HEADER_STYLE))

        cl = QLabel(f"{len(registry.list_plugins())} loaded", styleSheet=COUNT_STYLE)
        layout.addWidget(cl)

        self._table = QTableWidget()
        self._table.setColumnCount(3)
        self._table.setHorizontalHeaderLabels(["Name", "Version", "Description"])
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setShowGrid(False)
        self._table.verticalHeader().setVisible(False)
        self._table.setStyleSheet("""
            QTableWidget {
                background: transparent;
                border: none;
                font-size: 12px;
            }
            QTableWidget::item {
                color: #ebebf5;
                padding: 5px 8px;
                border: none;
            }
            QTableWidget::item:selected {
                background: rgba(100, 210, 255, 20);
            }
        """)
        layout.addWidget(self._table)

        plugins = registry.list_plugins()
        self._table.setRowCount(len(plugins))
        for i, plugin in enumerate(plugins):
            self._table.setItem(i, 0, QTableWidgetItem(plugin.name))
            self._table.setItem(i, 1, QTableWidgetItem(plugin.version))
            self._table.setItem(i, 2, QTableWidgetItem(plugin.description))
