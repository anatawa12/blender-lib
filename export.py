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


def export_for_unity(objs: List[Object], path: str):
    rotate_on_x(objs, -math.pi / 2)

    for o in objs:
        apply_transform(o)

    rotate_on_x(objs, math.pi / 2)

    export_fbx(objs, path)


def copy_join(objs: List[Object], name: str) -> Object:
    new_objs: List[Object] = cast(List[Object], [obj.copy() for obj in objs])
    new_objs[0].data = new_objs[0].data.copy()
    link_to_collection(new_objs, collection=cast(List[Collection], objs[0].users_collection)[0])
    new_objs[0].name = name
    merge_objects(new_objs)
    new_objs[0].parent = objs[0].parent
    return new_objs[0]


def link_to_collection(objs, collection: Collection = bpy.context.scene.collection):
    for obj in objs:
        cast(CollectionObjects, collection.objects).link(obj)


def merge_objects(objs):
    select_objects(objs)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join()


def select_objects(objs):
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objs:
        obj.select_set(True)


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
    bpy.ops.export_scene.fbx(
        use_selection=True,
        filepath=path,
        apply_scale_options='FBX_SCALE_ALL',
        object_types={'ARMATURE', 'MESH'},
        use_mesh_modifiers=True,
        mesh_smooth_type='EDGE',
        add_leaf_bones=False,
    )


def freeze_modifiers(obj: Object, modifiers: typing.Iterable[str]):
    select_objects([obj])
    for m in modifiers:
        bpy.ops.object.modifier_apply(modifier=m)


def merge_by_distance(obj: Object, threshold=0.0001):
    select_objects([obj])
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.remove_doubles(threshold=threshold)
    bpy.ops.object.mode_set(mode='OBJECT')


if __name__ == "__main__":
    main()
