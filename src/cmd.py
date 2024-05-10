from chimerax.core.commands import CmdDesc      # Command description
from .core import ChimeraX

def command_palette(session):
    chimerax = ChimeraX.instance(session)
    chimerax.show_command_palette()


DESC = CmdDesc(required=[], optional=[])
