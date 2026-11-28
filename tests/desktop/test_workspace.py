"""Presentation tests use the existing Core wire fixtures and lifecycle."""

from pathlib import Path
from uuid import uuid4

import pytest
from PySide6.QtCore import Qt
from PySide6.QtTest import QSignalSpy
from PySide6.QtWidgets import QApplication

from lineament_core.domain import ProjectRef
from lineament_core.lifecycle import JobLifecycle
from lineament_core.wire import decode_command
from lineament_desktop.workspace import LayerDisplay, ProjectWindow


@pytest.fixture(scope="module")
def app():
    application = QApplication.instance() or QApplication([])
    yield application


@pytest.fixture
def window(app):
    view = ProjectWindow("en")
    yield view
    view._busy = False
    view.close()
    view.deleteLater()
    app.processEvents()


def test_disabled_until_controller_and_project_available(window):
    assert all(not action.isEnabled() for action in window.actions.values())
    window.set_controller_ready(True)
    requested = QSignalSpy(window.new_requested)
    window.actions["new"].trigger()
    assert requested.count() == 1
    opened = QSignalSpy(window.open_requested)
    window.actions["open"].trigger()
    assert opened.count() == 1
    assert not window.actions["import"].isEnabled()
    window.show_project(ProjectRef(uuid4()), "Рельеф", ())
    assert window.actions["import"].isEnabled()
    imported = QSignalSpy(window.import_requested)
    window.actions["import"].trigger()
    assert imported.count() == 1
    assert "Рельеф" in window.windowTitle()


def test_metadata_and_reopen_clear_stale_selection(window):
    layer = LayerDisplay("DEM", "EPSG:32633", "m", "ft", "-9999", "int16")
    window.show_project(ProjectRef(uuid4()), "A", (layer,))
    window.layers.setCurrentItem(window.layers.topLevelItem(0))
    assert [window.properties.item(i, 1).text() for i in range(5)] == [
        "EPSG:32633",
        "m",
        "ft",
        "-9999",
        "int16",
    ]
    assert (
        not window.properties.item(0, 1).flags() & Qt.ItemFlag.ItemIsEditable
        or window.properties.editTriggers()
        == window.properties.EditTrigger.NoEditTriggers
    )
    window.show_project(ProjectRef(uuid4()), "B", ())
    assert window.layers.topLevelItemCount() == 0
    assert window.properties.rowCount() == 0


def test_actual_lifecycle_controls_cancellation_progress_and_close(window):
    fixtures = Path(__file__).parents[1] / "fixtures"
    lifecycle = JobLifecycle(decode_command((fixtures / "job.jsonl").read_bytes()))
    frames = (fixtures / "completed.jsonl").read_bytes().splitlines(keepends=True)
    window.set_controller_ready(True)
    window.show()
    lifecycle.accept_frame(frames[0])
    window.show_job(lifecycle)
    assert not window.close()
    assert not window.actions["new"].isEnabled()
    requested = QSignalSpy(window.cancel_requested)
    window.actions["cancel"].trigger()
    window.actions["cancel"].trigger()
    assert requested.count() == 1
    for frame in frames[1:3]:
        lifecycle.accept_frame(frame)
    window.show_job(lifecycle)
    assert window.progress.value() == 50
    assert not window.actions["cancel"].isEnabled()
    for frame in frames[3:]:
        lifecycle.accept_frame(frame)
    window.show_job(lifecycle)
    assert not window.close()  # terminal message arrives before process exit
    lifecycle.finish(0)
    window.show_job(lifecycle, process_exited=True)
    assert window.close()
    assert window.actions["new"].isEnabled()
    assert not window.actions["cancel"].isEnabled()


def test_russian_labels_and_problem_feedback(app):
    view = ProjectWindow("ru")
    assert view.actions["open"].text() == "Открыть проект"
    view.show_problem("Источник недоступен", warning=True)
    assert view.statusBar().currentMessage() == "Предупреждение — Источник недоступен"
    view.close()


def test_transport_failure_waits_for_process_cleanup(window):
    window.set_controller_ready(True)
    window.show()
    window.show_transport_failure("Worker stopped responding", process_exited=False)
    assert not window.close()
    assert not window.actions["cancel"].isEnabled()
    window.show_transport_failure("Worker exited", process_exited=True)
    assert window.close()
    assert window.actions["open"].isEnabled()
