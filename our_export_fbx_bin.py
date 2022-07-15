import bpy
from bpy.props import StringProperty
from bpy_extras.io_utils import (
        ImportHelper,
        ExportHelper,
        orientation_helper,
        path_reference_mode,
        axis_conversion,
        )
import datetime
from io_scene_fbx import (ExportFBX, export_fbx_bin)
from io_scene_fbx.export_fbx_bin import *
from .utils import ModifyAndRollback
import io_scene_fbx.fbx_utils
import hashlib
from types import SimpleNamespace

_keys_to_uuids = {}
_uuids_to_keys = {}


def _new_fbx_uuid_gen(key, uuids):
    if isinstance(key, int) and 0 <= key < 2 ** 63:
        uuid = key
    elif isinstance(key, str):
        uuid = int.from_bytes(hashlib.md5(key.encode()).digest()[:8], byteorder="big")
        if uuid < 0:
            uuid = -uuid
        if uuid >= 2**63:
            uuid //= 2
    else:
        raise Exception("unsupported type on uuid")
    if uuid > int(1e9):
        t_uuid = uuid % int(1e9)
        if t_uuid not in uuids:
            uuid = t_uuid

    # Make sure our uuid *is* unique.
    if uuid in uuids:
        inc = 1 if uuid < 2**62 else -1
        while uuid in uuids:
            uuid += inc
            if 0 > uuid >= 2**63:
                # Note that this is more that unlikely, but does not harm anyway...
                raise ValueError("Unable to generate an UUID for key {}".format(key))

    return fbx_utils.UUID(uuid)


def _fbx_uuid_from_key(key):
    uuid = _keys_to_uuids.get(key)
    if uuid is None:
        uuid = _new_fbx_uuid_gen(key, _uuids_to_keys)
        _keys_to_uuids[key] = uuid
        _uuids_to_keys[uuid] = key
    return uuid


def _fbx_key_from_uuid(uuid):
    """
    Return the key which generated this uid.
    """
    assert(uuid.__class__ == fbx_utils.UUID)
    return _uuids_to_keys.get(uuid, None)


def export_fbx(*args, **kwargs):
    with ModifyAndRollback() as modify:
        modify.add_modify(fbx_utils, "get_key_from_fbx_uuid", _fbx_key_from_uuid)
        modify.add_modify(fbx_utils, "get_fbx_uuid_from_key", _fbx_uuid_from_key)
        modify.add_modify(export_fbx_bin, "get_fbx_uuid_from_key", _fbx_uuid_from_key)

        kwargs_copy = kwargs.copy()
        time = kwargs_copy.get("time")
        if time is not None:
            time = datetime.datetime.fromisoformat(time)
            datetime_now_wrap = lambda: time
            datetime_cls_wrap = SimpleNamespace()
            datetime_cls_wrap.now = datetime_now_wrap
            datetime_mod_wrap = SimpleNamespace()
            datetime_mod_wrap.datetime = datetime_cls_wrap
            modify.add_modify(export_fbx_bin, "datetime", datetime_mod_wrap)
            del kwargs_copy["time"]

        return bpy.ops.export_scene.fbx(*args, **kwargs_copy)
