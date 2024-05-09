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
        palette.set_max_rows(500)
        
        for child in self._main_window.menuBar().children():
            if not isinstance(child, QtW.QMenu):
                continue
            group_name = child.title().replace("&", "")
            if group_name == "":
                continue
            group = palette.add_group(child.title().replace("&", ""))
            for action, context in iter_action(child):
                group.register(
                    make_command(action), 
                    desc=" > ".join([*context, action.text()]).replace("&", ""),
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

def iter_action(menu: QtW.QMenu, cur=None) -> Iterator[tuple[QtW.QAction, list[str]]]:
    cur = cur or []
    for ac in menu.actions():
        parent = ac.parent()
        if parent is menu:
            continue
        if isinstance(parent, QtW.QMenu):
            yield from iter_action(ac.parent(), cur=[*cur, ac.text()])
        else:
            yield ac, cur

def make_command(action: QtW.QAction):
    return lambda: action.trigger()
