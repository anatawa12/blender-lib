import typing
from typing import Dict, cast, List, Optional

import bpy
from bpy.types import Object, Mesh, MeshPolygon, Material, IDMaterials, BlendDataMaterials, MeshUVLoop, UVLoopLayers

from .utils import UVRegion, select_objects


def remove_face_of_materials(
        obj: Object,
        remove_mat: str,
):
    mesh = obj.data
    if not isinstance(mesh, Mesh):
        raise Exception("object is not mesh")

    mat_index: Optional[int] = None

    for index, material in enumerate(cast(List[Material], mesh.materials)):
        if remove_mat == material.name:
            mat_index = index

    if mat_index is None:
        raise Exception(f"material named {remove_mat} not found")

    for poly in cast(List[MeshPolygon], mesh.polygons):
        if poly.material_index != mat_index:
            continue
        poly.select = True
        pass

    bpy.ops.object.mode_set_with_submode(mode='EDIT', mesh_select_mode={'FACE'})
    bpy.ops.mesh.delete(type='FACE')
    bpy.ops.object.mode_set(mode='OBJECT')
    remove_material(mesh, remove_mat)


def merge_materials(
        obj: Object,
        region_mapping: Dict[str, UVRegion],
        final_material: str,
):
    mesh = obj.data
    if not isinstance(mesh, Mesh):
        raise Exception("object is not mesh")

    region_mapping_by_index: Dict[int, UVRegion] = {}
    final_material_index: Optional[int] = None

    for index, material in enumerate(cast(List[Material], mesh.materials)):
        region = region_mapping.get(material.name)
        if region is not None:
            region_mapping_by_index[index] = region
        if final_material == material.name:
            final_material_index = index

    if final_material_index is None:
        found_mat = cast(Dict[str, Material], bpy.data.materials).get(final_material)
        if found_mat is None:
            found_mat = cast(BlendDataMaterials, bpy.data.materials).new(final_material)
        cast(IDMaterials, mesh.materials).append(found_mat)
        final_material_index = len(cast(List[Material], mesh.materials)) - 1

    uv_loops = cast(List[MeshUVLoop], cast(UVLoopLayers, mesh.uv_layers).active.data)  # TODO: selectable by param

    for poly in cast(List[MeshPolygon], mesh.polygons):
        region = region_mapping_by_index.get(poly.material_index)
        if region is None:
            continue
        for loop_idx in cast(range, poly.loop_indices):
            loop = uv_loops[loop_idx]
            loop.uv = [*region.fit_from_1x1(*loop.uv)]
        poly.material_index = final_material_index
        pass

    for mat_name in region_mapping.keys():
        remove_material(mesh, mat_name)


def remove_material(mesh: Mesh, name: str):
    mats = cast(IDMaterials, mesh.materials)
    for index, mat in enumerate(cast(typing.Iterable[Material], mats)):
        if mat.name == name:
            mats.pop(index = index)
            return


def simple_merge_materials(obj: Object, merge_from: List[str], merge_to: str):
    select_objects([obj])
    bpy.ops.object.mode_set(mode='EDIT')

    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')

    from_indices = [obj.material_slots[mat_name].slot_index for mat_name in merge_from]
    to_index = obj.material_slots[merge_to].slot_index

    for mat_indices in from_indices:
        bpy.context.object.active_material_index = mat_indices
        bpy.ops.object.material_slot_select()

    bpy.context.object.active_material_index = to_index
    bpy.ops.object.material_slot_assign()

    bpy.ops.object.mode_set(mode='OBJECT')

    for mat_indices in from_indices:
        bpy.context.object.active_material_index = mat_indices
        bpy.ops.object.material_slot_select()
