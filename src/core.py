from __future__ import annotations

from typing import TYPE_CHECKING, Iterator

from qtpy import QtWidgets as QtW

from qt_command_palette import get_palette

if TYPE_CHECKING:
    from chimerax.core.session import Session

class ChimeraX:
    _session: Session | None = None
    _instance: ChimeraX | None = None
    
    def __init__(self, session):
        self.__class__._session = session
        self._palette = self.install_command()
        self.__class__._instance = self
    
    @property
    def session(self) -> Session:
        """Get the ChimeraX session"""
        return self._session

    @property
    def _main_window(self) -> QtW.QMainWindow:
        return self.session.ui.main_window
    
    def install_command(self):
        palette = get_palette("ChimeraX", alignment="screen")

        # Add menu actions
        for child in self._main_window.menuBar().children():
            if not isinstance(child, QtW.QMenu):
                continue
            group_name = child.title().replace("&", "")
            if group_name == "":
                continue
            group = palette.add_group(child.title().replace("&", ""))
            for action, context in iter_actions(child):
                group.register(
                    make_command(action), 
                    desc=" > ".join([*context, action.text()]).replace("&", ""),
                    tooltip=action.toolTip(),
                )
        # Add toolbar actions
        toolbar_group = palette.add_group("Toolbar")
        for action, context in iter_toolbar_actions(self._main_window):
            toolbar_group.register(
                make_command(action), 
                desc=" > ".join(context),
                tooltip=action.toolTip(),
            )
    
        palette.install(self._main_window)
        return palette

    def show_command_palette(self):
        self._palette.show_widget(self._main_window)

    @classmethod
    def instance(cls, session) -> ChimeraX:
        if cls._instance is None:
            cls(session)
        return cls._instance

def iter_actions(menu: QtW.QMenu, cur=None) -> Iterator[tuple[QtW.QAction, list[str]]]:
    cur = cur or []
    for ac in menu.actions():
        parent = ac.parent()
        if parent is menu:
            continue
        if isinstance(parent, QtW.QMenu):
            yield from iter_actions(ac.parent(), cur=[*cur, ac.text()])
        else:
            yield ac, cur

def make_command(action: QtW.QAction):
    return lambda: action.trigger()

def iter_toolbar_actions(
    main_window: QtW.QMainWindow,
) -> Iterator[tuple[QtW.QAction, list[str]]]:
    
    tabbed = _find_tabbed_toolbar(main_window)
    for i in range(tabbed.count()):
        tab_name = tabbed.tabText(i)
        toolbar = tabbed.widget(i)
        for child in toolbar.children():
            if type(child) is QtW.QWidget:
                label_widget = _find_label_widget(child)
                if label_widget is None:
                    for action in _iter_toolbutton_action(child):
                        text = action.text().replace("\n", " ")
                        yield action, [tab_name, text]
                else:
                    label = label_widget.text()
                    for action in _iter_toolbutton_action(child):
                        text = action.text().replace("\n", " ")
                        yield action, [tab_name, label, text]

def _find_tabbed_toolbar(main_window: QtW.QMainWindow) -> QtW.QTabWidget:
    """Find the TabbedToolBar in the ChimeraX main window"""
    tb: QtW.QWidget | None = None
    for c in main_window.children():
        if isinstance(c, QtW.QDockWidget):
            if c.windowTitle() == "Toolbar":
                tb = c.widget()
                break
    if tb is None:
        raise ValueError("Toolbar not found")
    ttb = tb.children()[1].children()[0]
    
    if not isinstance(ttb, QtW.QTabWidget):
        raise ValueError("Tabbed toolbar not found")
    return ttb

def _find_label_widget(widget: QtW.QWidget) -> QtW.QLabel | None:
    """Find the label widget in a section widget."""
    children = widget.children()
    for child in children:
        if isinstance(child, QtW.QLabel):
            return child
    return None

def _iter_toolbutton_action(widget: QtW.QWidget):
    for child in widget.children():
        if isinstance(child, QtW.QToolButton):
            actions = child.actions()
            if len(actions) > 0:
                yield actions[0]
