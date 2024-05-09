from __future__ import annotations

from chimerax.core.toolshed import BundleAPI

class _MyAPI(BundleAPI):

    api_version = 1

    # Override method
    
    # Override method for defining presets
    @staticmethod
    def register_command(bi, ci, logger):
        from . import cmd
        if not ci.name == "command palette":
            return
        
        from chimerax.core.commands import register
        register(ci.name, cmd.DESC, cmd.command_palette)

    @staticmethod
    def get_class(class_name):
        pass

bundle_api = _MyAPI()
