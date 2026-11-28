"""Project presentation with controller-owned IO and Core-owned job lifecycle.

A controller supplies display records after validating the project in the Worker.
Intent signals do no IO. Keep actions disabled until a controller is connected.
"""

from dataclasses import dataclass

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction, QCloseEvent, QKeySequence
from PySide6.QtWidgets import (
    QDockWidget,
    QLabel,
    QMainWindow,
    QProgressBar,
    QTableWidget,
    QTableWidgetItem,
    QToolBar,
    QTreeWidget,
    QTreeWidgetItem,
)

from lineament_core.domain import ProjectRef
from lineament_core.lifecycle import JobLifecycle, JobState

_TEXT = {
    "en": {
        "new": "New project",
        "open": "Open project",
        "import": "Import DEM",
        "cancel": "Cancel",
        "layers": "Layers and results",
        "properties": "Properties",
        "empty": "Open or create a project",
        "project": "Select a layer to inspect its metadata",
        "field": "Property",
        "value": "Value",
        "crs": "CRS",
        "horizontal": "Horizontal unit",
        "vertical": "Vertical unit",
        "nodata": "NoData",
        "dtype": "Data type",
        "busy": "Wait for the active task to finish before closing",
        "pending": "Waiting",
        "running": "Running",
        "cancel_requested": "Cancellation requested",
        "committing": "Saving result",
        "cancelled": "Cancelled",
        "failed": "Failed",
        "completed": "Completed",
        "warning": "Warning",
        "error": "Error",
        "unavailable": "Controller connection required",
        "missing": "Not specified",
    },
    "ru": {
        "new": "Новый проект",
        "open": "Открыть проект",
        "import": "Импорт DEM",
        "cancel": "Отмена",
        "layers": "Слои и результаты",
        "properties": "Свойства",
        "empty": "Откройте или создайте проект",
        "project": "Выберите слой для просмотра метаданных",
        "field": "Свойство",
        "value": "Значение",
        "crs": "CRS",
        "horizontal": "Горизонтальные единицы",
        "vertical": "Вертикальные единицы",
        "nodata": "NoData",
        "dtype": "Тип данных",
        "busy": "Дождитесь завершения активного задания перед закрытием",
        "pending": "Ожидание",
        "running": "Выполняется",
        "cancel_requested": "Запрошена отмена",
        "committing": "Сохранение результата",
        "cancelled": "Отменено",
        "failed": "Ошибка задания",
        "completed": "Завершено",
        "warning": "Предупреждение",
        "error": "Ошибка",
        "unavailable": "Требуется подключение контроллера",
        "missing": "Не указано",
    },
}


@dataclass(frozen=True, slots=True)
class LayerDisplay:
    """UI-only text fields supplied by the project controller, never persisted."""

    label: str
    crs: str | None = None
    horizontal_unit: str | None = None
    vertical_unit: str | None = None
    nodata: str | None = None
    dtype: str | None = None


class ProjectWindow(QMainWindow):
    """Thin Qt view. Bind intents before calling set_controller_ready(True)."""

    new_requested = Signal()
    open_requested = Signal()
    import_requested = Signal()
    cancel_requested = Signal()

    def __init__(self, language: str = "ru") -> None:
        super().__init__()
        self.text = _TEXT[language]
        self.project: ProjectRef | None = None
        self._controller_ready = False
        self._busy = False
        self._cancellable = False
        self._cancel_sent = False
        self.setWindowTitle("Lineament Studio")
        self.resize(1100, 720)
        toolbar = QToolBar(self)
        toolbar.setObjectName("projectToolbar")
        self.addToolBar(toolbar)
        self.actions = {}
        for key, signal in (
            ("new", self.new_requested),
            ("open", self.open_requested),
            ("import", self.import_requested),
        ):
            action = QAction(self.text[key], self)
            action.triggered.connect(signal.emit)
            toolbar.addAction(action)
            self.actions[key] = action
        self.actions["new"].setShortcut(QKeySequence.StandardKey.New)
        self.actions["open"].setShortcut(QKeySequence.StandardKey.Open)
        self.actions["cancel"] = QAction(self.text["cancel"], self)
        self.actions["cancel"].triggered.connect(self._request_cancel)
        toolbar.addAction(self.actions["cancel"])
        self.message = QLabel(self.text["empty"])
        self.message.setTextFormat(Qt.TextFormat.PlainText)
        self.message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCentralWidget(self.message)
        self.layers = QTreeWidget()
        self.layers.setHeaderLabel(self.text["layers"])
        self.layers.currentItemChanged.connect(self._show_layer)
        self.properties = QTableWidget(0, 2)
        self.properties.setHorizontalHeaderLabels(
            [self.text["field"], self.text["value"]]
        )
        self.properties.horizontalHeader().setStretchLastSection(True)
        self.properties.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        for name, widget, area in (
            ("layers", self.layers, Qt.DockWidgetArea.LeftDockWidgetArea),
            ("properties", self.properties, Qt.DockWidgetArea.RightDockWidgetArea),
        ):
            dock = QDockWidget(self.text[name], self)
            dock.setObjectName(name)
            dock.setWidget(widget)
            self.addDockWidget(area, dock)
        self.progress = QProgressBar()
        self.progress.hide()
        self.statusBar().addPermanentWidget(self.progress)
        self._update_actions()

    def set_controller_ready(self, ready: bool) -> None:
        self._controller_ready = ready
        self._update_actions()

    def show_project(
        self, project: ProjectRef, title: str, layers: tuple[LayerDisplay, ...]
    ) -> None:
        """Render a validated immutable display snapshot on the Qt thread."""
        self.project = project
        self.setWindowTitle(f"{title} — Lineament Studio")
        self.layers.clear()
        self.properties.setRowCount(0)
        for layer in layers:
            item = QTreeWidgetItem([layer.label])
            item.setData(0, Qt.ItemDataRole.UserRole, layer)
            self.layers.addTopLevelItem(item)
        self.message.setText(self.text["project"])
        self._update_actions()

    def show_job(
        self, lifecycle: JobLifecycle, *, process_exited: bool = False
    ) -> None:
        """Render Core state; controller confirms process exit after lifecycle.finish()."""
        state = lifecycle.state
        terminal = state in (JobState.COMPLETED, JobState.FAILED, JobState.CANCELLED)
        self._busy = not (terminal and process_exited)
        self._cancellable = state is JobState.RUNNING
        if terminal or state is JobState.PENDING:
            self._cancel_sent = False
        self.statusBar().showMessage(self.text[state.value])
        self.progress.setVisible(self._busy)
        if lifecycle.progress is None:
            self.progress.setRange(0, 0)
        else:
            self.progress.setRange(0, 100)
            self.progress.setValue(lifecycle.progress)
        self._update_actions()

    def show_transport_failure(self, message: str, *, process_exited: bool) -> None:
        """Controller reports a failed exchange and whether its process is reaped."""
        self._busy = not process_exited
        self._cancellable = False
        self.progress.setVisible(self._busy)
        self.show_problem(message)
        self._update_actions()

    def show_problem(self, message: str, *, warning: bool = False) -> None:
        kind = "warning" if warning else "error"
        self.statusBar().showMessage(f"{self.text[kind]} — {message}")

    def _request_cancel(self) -> None:
        if self._cancellable and not self._cancel_sent:
            self._cancel_sent = True
            self._update_actions()
            self.cancel_requested.emit()

    def _update_actions(self) -> None:
        ready = self._controller_ready and not self._busy
        self.actions["new"].setEnabled(ready)
        self.actions["open"].setEnabled(ready)
        self.actions["import"].setEnabled(ready and self.project is not None)
        self.actions["cancel"].setEnabled(
            self._controller_ready and self._cancellable and not self._cancel_sent
        )
        for action in self.actions.values():
            action.setToolTip(
                action.text() if self._controller_ready else self.text["unavailable"]
            )

    def _show_layer(self, current, previous) -> None:
        self.properties.setRowCount(0)
        if current is None:
            return
        layer = current.data(0, Qt.ItemDataRole.UserRole)
        fields = (
            ("crs", layer.crs),
            ("horizontal", layer.horizontal_unit),
            ("vertical", layer.vertical_unit),
            ("nodata", layer.nodata),
            ("dtype", layer.dtype),
        )
        for row, (key, value) in enumerate(fields):
            self.properties.insertRow(row)
            self.properties.setItem(row, 0, QTableWidgetItem(self.text[key]))
            self.properties.setItem(
                row,
                1,
                QTableWidgetItem(value if value is not None else self.text["missing"]),
            )

    def closeEvent(self, event: QCloseEvent) -> None:
        if self._busy:
            event.ignore()
            self.statusBar().showMessage(self.text["busy"])
        else:
            super().closeEvent(event)
