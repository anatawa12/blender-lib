import typing
from typing import Dict, cast, List, Optional, Set

import bpy
from bpy.types import Object, Mesh, MeshPolygon, Material, IDMaterials, BlendDataMaterials, MeshUVLoop, UVLoopLayers, VertexGroup, MeshVertex, VertexGroupElement

from .utils import UVRegion
from .export import select_objects

def remove_face_of_group(
        obj: Object,
        vertex_group: str,
):
    mesh = obj.data
    if not isinstance(mesh, Mesh):
        raise Exception("object is not mesh")

    vertex_group_idx = cast(Dict[str, VertexGroup], obj.vertex_groups)[vertex_group].index
    vertices: Set[int] = set()

    for v in cast(List[MeshVertex], mesh.vertices):
        for g in cast(List[VertexGroupElement],  v.groups):
            if g.group == vertex_group_idx:
                vertices.add(v.index)
                break

    for poly in cast(List[MeshPolygon], mesh.polygons):
        poly.select = False
        for v in cast(List[MeshVertex], poly.vertices):
            if v not in vertices:
                break
        else:
            # if all elements are in vertex_group
            poly.select = True
        pass

    # remove selected faces
    select_objects([obj])
    bpy.ops.object.mode_set_with_submode(mode='EDIT', mesh_select_mode={'FACE'})
    bpy.ops.mesh.delete(type='FACE')
    bpy.ops.object.mode_set(mode='OBJECT')
