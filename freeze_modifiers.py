import typing
from typing import List, cast, Dict
from bpy.types import Object, Collection, CollectionObjects, Mesh
from .utils import select_objects, delete_objects, link_to_collection
import bpy


def freeze_modifiers(obj: Object, modifiers: typing.Iterable[str]):
    if obj.data.shape_keys is None:
        _do_freeze_modifiers(obj, modifiers)
    else:
        result = _clone(obj)
        _clear_shape_keys(result, 'Basis')
        _do_freeze_modifiers(result, modifiers)

        for i in range(1, len(obj.data.shape_keys.key_blocks)):
            shape_name = obj.data.shape_keys.key_blocks[i].name
            obj_tmp = _clone(obj)

            _clear_shape_keys(obj_tmp, shape_name)

            _do_freeze_modifiers(obj_tmp, modifiers)

            select_objects([result, obj_tmp])

            bpy.ops.object.join_shapes()
            result.data.shape_keys.key_blocks[-1].name = shape_name

            delete_objects([obj_tmp])

        tmp_name = obj.name
        tmp_data_name = obj.data.name
        result.name = tmp_name + '.tmp'

        obj.data = result.data
        obj.data.name = tmp_data_name

        for x in modifiers:
            obj.modifiers.remove(obj.modifiers[x])

        delete_objects([result])
        pass


def _do_freeze_modifiers(obj: Object, modifiers: typing.Iterable[str]):
    select_objects([obj])
    for m in modifiers:
        bpy.ops.object.modifier_apply(modifier=m)


def _clear_shape_keys(obj: Object, keep: str):
    select_objects([obj])
    if obj.data.shape_keys is None:
        return True

    obj.active_shape_key_index = len(obj.data.shape_keys.key_blocks) - 1
    while len(obj.data.shape_keys.key_blocks) > 1:
        if obj.data.shape_keys.key_blocks[obj.active_shape_key_index].name == keep:
            obj.active_shape_key_index = 0
        else:
            bpy.ops.object.shape_key_remove()

    bpy.ops.object.shape_key_remove()


def _clone(obj):
    tmp_obj = obj.copy()
    tmp_obj.data = tmp_obj.data.copy()
    obj.users_collection[0].objects.link(tmp_obj)
    return tmp_obj
