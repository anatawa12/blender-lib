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

import typing
from typing import List, cast, Dict

import bpy
import math
import mathutils

from bpy.types import Object, Collection, CollectionObjects
from .utils import select_objects, copy_join, link_to_collection, merge_objects
from .freeze_modifiers import freeze_modifiers


def export_for_unity(objs: List[Object], path: str):
    export_fbx(objs, path)


def objects_from_names(names: List[str]) -> List[Object]:
    return [cast(Dict[str, 'Object'], bpy.data.objects)[name] for name in names]


def rotate_on_x(objs: List[Object], theta: float) -> None:
    select_objects(objs)
    bpy.context.scene.tool_settings.transform_pivot_point = 'BOUNDING_BOX_CENTER'
    bpy.ops.transform.rotate(
        value=theta,
        orient_axis='X',
        orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)),  # type: ignore
        constraint_axis=[True, False, False],
        mirror=True,
    )


def symmetrize_armature(obj: Object):
    select_objects([obj])
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.armature.select_all(action='SELECT')
    bpy.ops.armature.symmetrize()
    bpy.ops.object.mode_set(mode='OBJECT')


def apply_transform(obj: Object):
    mat = obj.matrix_basis
    if isinstance(obj.data, bpy.types.Mesh):
        obj.data.transform(mat, shape_keys=True)
    elif hasattr(obj.data, "transform"):
        obj.data.transform(mat)  # type: ignore
    else:
        print("can't transform: " + str(obj) + " (" + str(type(obj.data)) + ")")

    for c in cast(typing.Iterable[Object], obj.children):
        c.matrix_local = c.matrix_local @ mat  # type: ignore
    obj.matrix_basis = mathutils.Matrix.Identity(4)  # type: ignore


def hide_all(objs):
    for o in objs:
        o.hide_set(False)


def export_fbx(objs, path):
    select_objects(objs)
    from .our_export_fbx_bin import export_fbx
    export_fbx(
        # General
        filepath=path,
        # Include
        use_selection=True,
        use_visible=False,
        use_active_collection=False,
        object_types={'ARMATURE', 'MESH'},
        use_custom_props=False,
        # Transform
        global_scale=1.0,
        apply_scale_options='FBX_SCALE_ALL',
        axis_forward='-Z',
        axis_up='Y',
        apply_unit_scale=True,  # Apply Unit
        use_space_transform=True,  # Use Space Transform
        bake_space_transform=True,  # Apply Transform
        # Geometry
        mesh_smooth_type='OFF',
        use_subsurf=False,
        use_mesh_modifiers=True,  # Apply Modifiers
        use_mesh_edges=False,  # Loose Edges
        use_triangles=False,  # Triangulate Faces
        use_tspace=False,  # Tangent Space
        # Armature
        primary_bone_axis='Y',
        secondary_bone_axis='X',
        armature_nodetype='NULL',  # Armature FBXNode Type
        use_armature_deform_only=False,  # Only Deform Bones
        add_leaf_bones=False,  # Add Leaf Bones
        # Bake Animation
        bake_anim=True,
        bake_anim_use_all_bones=True,  # Key All Bones
        bake_anim_use_nla_strips=True,  # NLA Strips
        bake_anim_use_all_actions=True,  # All Actions
        bake_anim_force_startend_keying=True,  # Force Start/End Keying
        bake_anim_step=1.0,  # Sampling Rate
        bake_anim_simplify_factor=1.0,  # Simplify
        # Anatawa12's part
        time="1970-01-01T00:00:00+00:00:00",
    )


def merge_by_distance(obj: Object, threshold=0.0001):
    select_objects([obj])
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.remove_doubles(threshold=threshold)
    bpy.ops.object.mode_set(mode='OBJECT')
