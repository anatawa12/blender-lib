import bpy

_context: bpy.types.Context = bpy.context  # type: ignore


def context():
    return _context


def set_context(new_context: bpy.types.Context):
    global _context
    _context = new_context

