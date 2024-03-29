# anatawa12's blender libraries
# Copyright (c) 2022 anatawa12
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/gpl-3.0.html>.


# noinspection PyUnresolvedReferences
from .uv_semi_mirror import mirror_uv
# noinspection PyUnresolvedReferences
from .utils import Axis, UVRegion
# noinspection PyUnresolvedReferences
from .export import copy_join, export_for_unity, freeze_modifiers, merge_by_distance, symmetrize_armature
# noinspection PyUnresolvedReferences
from .materials import merge_materials, remove_material, remove_face_of_materials, simple_merge_materials
# noinspection PyUnresolvedReferences
from .faces import remove_face_of_group
from .output_file_chooser import ask_export

bl_info = {
    "name": "anatawa12's library",
    "author": "anatawa12",
    "version": (0, 0),
    "blender": (3, 2, 0),
    "location": "",
    "description": "anatawa12's library",
    "warning": "",
    "support": "TESTING",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Object",
    "anatawa12_library_selector": 7,
}


def register():
    print("register of anatawa12's library")


def unregister():
    print("unregister of anatawa12's library")


def version_check(v: int):
    supported_minimum = 1
    if supported_minimum <= v <= bl_info["anatawa12_library_selector"]:  # type: ignore
        return
    import bpy
    bpy.context.window_manager.popup_menu(
        (lambda s, c: s.layout.label(text="Please install anatawa12's blender library version %d" % v)),
        title="Error", icon='ERROR')


def enable_cats_blender_plugin():
    from .utils import find_enable_addon
    find_enable_addon('Cats Blender Plugin')

