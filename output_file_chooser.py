import sys
import typing

import bpy
import os
from bpy_extras.io_utils import ImportHelper, ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator, Context
import uuid


def ask_export(
        callback: typing.Callable[[str], None],
        label: str,
        extension: str = '',
):
    if "--anatawa12-output" in sys.argv:
        callback(sys.argv[sys.argv.index("--anatawa12-output") + 1])
        return

    idname = uuid.uuid4().hex

    class Exporter(Operator, ExportHelper):
        """This appears in the tooltip of the operator and in the generated docs"""
        bl_idname = 'anatawa12lib.' + idname
        bl_label = label

        # ImportHelper mixin class uses this
        filename_ext = extension

        def execute(self, context: Context):
            callback(self.filepath)

            bpy.utils.unregister_class(Exporter)

            return {'FINISHED'}

        def cancel(self, context: Context):
            bpy.utils.unregister_class(Exporter)

    bpy.utils.register_class(Exporter)
    getattr(bpy.ops.anatawa12lib, idname)('INVOKE_DEFAULT')
