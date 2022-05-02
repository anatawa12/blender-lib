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

from typing import Optional, cast, Dict, List, Callable, FrozenSet, Set, Tuple, Iterable, TypeVar, Container, Sequence

from bpy.types import Object, Mesh, VertexGroup, MeshVertex, VertexGroupElement, MeshPolygon, UVLoopLayers, MeshUVLoop
from .utils import Axis, flip_name


def mirror_uv(
        src_obj: Object,
        dst_obj_in: Optional[Object] = None,
        src_vertex_group: Optional[str] = None,
        dst_vertex_group: Optional[str] = None,
        obj_mirror_axis: Axis = Axis.X,
        obj_mirror_origin: float = 0,  # mirror origin
        obj_ignore_axis: Optional[Axis] = None,  # if some axis should be ignored on homologous vertex search
        uv_mirror_axis: Optional[Axis] = None,  # None if not mapped
        uv_mirror_origin: float = 0.5,  # mirror origin
        mirror_vertex_group: bool = False,
):
    dst_obj: Object = dst_obj_in if dst_obj_in is not None else src_obj
    src_mesh = cast(Mesh, src_obj.data)
    dst_mesh = cast(Mesh, dst_obj.data)
    src_vertices = [v for v in cast(List['MeshVertex'], src_mesh.vertices)]
    dst_vertices = [v for v in cast(List['MeshVertex'], dst_mesh.vertices)]
    src_vertex_indices = _get_vertex_indices(src_obj, src_mesh, src_vertex_group)
    dst_vertex_indices = _get_vertex_indices(dst_obj, dst_mesh, dst_vertex_group)
    if len(src_vertex_indices) != len(dst_vertex_indices):
        raise Exception(f"The count of vertex mismatch: src: {len(src_vertex_indices)}, dst: {len(dst_vertex_indices)}")

    idx_mapping: Dict[int, int] = _make_vertex_mapping(
        src_vertices,
        dst_vertices,
        src_vertex_indices,
        dst_vertex_indices,
        _vertex_distance_squared_computer(obj_mirror_axis, obj_mirror_origin, obj_ignore_axis),
    )

    dst_polys = _collect_polygons(cast(List[MeshPolygon], dst_mesh.polygons), dst_vertex_indices, lambda a: idx_mapping[a])
    src_polys = _collect_polygons(cast(List[MeshPolygon], src_mesh.polygons), src_vertex_indices)

    src_uv_layer = cast(List[MeshUVLoop],
                        cast(UVLoopLayers, src_mesh.uv_layers).active.data)  # TODO: selectable by param
    dst_uv_layer = cast(List[MeshUVLoop],
                        cast(UVLoopLayers, dst_mesh.uv_layers).active.data)  # TODO: selectable by param

    if len(dst_polys) != len(src_polys):
        raise Exception("polys count mismatch")

    uv_mirror_origin = (uv_mirror_origin + 1) / 2

    for vertices, dst_polys1 in dst_polys.items():
        src_polys1 = src_polys[vertices]
        if src_polys1 is None:
            raise Exception(f"src_polys1")
        for (dst_poly, _), (src_poly, _), offset in _all_matched(dst_polys1, src_polys1):
            for dst_i, src_i in zip(
                    cast(range, dst_poly.loop_indices),
                    _offset([i for i in reversed(cast(range, src_poly.loop_indices))], offset)):
                dst_uv_layer[dst_i].uv = _invert_uv(src_uv_layer[src_i].uv, uv_mirror_axis, uv_mirror_origin)
    if mirror_vertex_group:
        for i, dst_vertex in enumerate(dst_vertices):
            src_vertex_index = idx_mapping.get(i)
            if src_vertex_index is None:
                continue
            src_vertex = src_vertices[idx_mapping[i]]
            for dst_group in cast(Iterable[VertexGroupElement], dst_vertex.groups):
                cast(List[VertexGroup], dst_obj.vertex_groups)[dst_group.group].remove([dst_vertex.index])

            for src_group in cast(Iterable[VertexGroupElement], src_vertex.groups):
                src_group_name = cast(List[VertexGroup], src_obj.vertex_groups)[src_group.group].name
                dst_group_name_candidates = _flip_name_candidates(src_group_name)
                for dst_group_name_candidate in dst_group_name_candidates:
                    dst_group_candidate = cast(Dict[str, VertexGroup], src_obj.vertex_groups)\
                        .get(dst_group_name_candidate)
                    if dst_group_candidate is not None:
                        dst_group_candidate.add([dst_vertex.index], weight=src_group.weight, type="ADD")
                        break


def _collect_polygons(
        polygons: List[MeshPolygon],
        vertex_indices: Container[int],
        keymap: Callable[[int], int] = lambda a: a,
) -> Dict[FrozenSet[int], Set[Tuple[MeshPolygon, Tuple[int, ...]]]]:
    mapping: Dict[FrozenSet[int], Set[Tuple[MeshPolygon, Tuple[int, ...]]]] = {}
    for p in polygons:
        if not _contains_all(p.vertices, vertex_indices):
            continue
        vertices = tuple(keymap(k) for k in p.vertices)
        key = frozenset(vertices)
        if key not in mapping:
            mapping[key] = set()
        mapping[key].add((p, vertices))
    return mapping


def _make_vertex_mapping(
        src_vertices: List[MeshVertex],
        dst_vertices: List[MeshVertex],
        src_vertex_indices: FrozenSet[int],
        dst_vertex_indices: FrozenSet[int],
        dist_sq_computer: Callable[[MeshVertex, MeshVertex], float],
) -> Dict[int, int]:
    """
        create dst and src index mapping
        this is dst -> src mapping because it should be fast to check if the found dst is already found or not
    """
    # create dst and src index mapping
    # this is dst -> src mapping because it should be fast to check if the found dst is already found or not
    idx_mapping: Dict[int, int] = {}
    for src_vertex_idx in src_vertex_indices:
        src_vertex = src_vertices[src_vertex_idx]
        iterator = iter(dst_vertex_indices)
        best_idx = next(iterator)
        best_dist_sq = dist_sq_computer(dst_vertices[best_idx], src_vertex)
        for dst_vertex_idx in iterator:
            dist_sq = dist_sq_computer(dst_vertices[dst_vertex_idx], src_vertex)
            if dist_sq < best_dist_sq:
                best_dist_sq = dist_sq
                best_idx = dst_vertex_idx

        if best_idx in idx_mapping:
            raise Exception(
                f"nearest vertex duplicated: #{best_idx} is for #{src_vertex_idx} and #{idx_mapping[best_idx]}")
        idx_mapping[best_idx] = src_vertex_idx
    return idx_mapping


def _all_matched(
        a_iterable: Iterable[Tuple[MeshPolygon, Tuple[int, ...]]],
        b_iterable: Iterable[Tuple[MeshPolygon, Tuple[int, ...]]],
) -> Iterable[Tuple[Tuple[MeshPolygon, Tuple[int, ...]], Tuple[MeshPolygon, Tuple[int, ...]], int]]:
    a_set = set(a_iterable)
    b_set = set(b_iterable)
    b_returned = set()
    for a in a_set:
        found = False
        for b in b_set:
            offset = _match_poly(a[1], b[1])
            if offset is None:
                continue
            if found or (b in b_returned):
                raise Exception("multiple polygon matched")
            b_returned.add(b)
            yield a, b, offset
            found = True


def _match_poly(a: Tuple[int, ...], b: Tuple[int, ...]) -> Optional[int]:
    if len(a) != len(b):
        return None
    al = [*a]
    bl = [*b]

    bl.reverse()

    for i in range(0, len(al)):
        if al == bl:
            return i
        bl = [*bl[1::], bl[0]]

    return None


def _get_vertex_indices(obj: Object, mesh: Mesh, vertex_group: Optional[str]) -> FrozenSet[int]:
    vertices = cast(List['MeshVertex'], mesh.vertices)
    if vertex_group is None:
        return frozenset([i for i in range(0, len(vertices))])
    group_index = cast(Dict[str, VertexGroup], obj.vertex_groups)[vertex_group].index
    if group_index is None:
        raise Exception(f"Vertex group {vertex_group} not found")
    l: List[int] = []
    for i, v in enumerate(vertices):
        for group in cast(List[VertexGroupElement], v.groups):
            if group.group == group_index:
                l.append(i)
    return frozenset(l)


def _vertex_distance_squared_computer(
        mirror_axis: Axis = Axis.X,
        mirror_origin: float = 0,  # mirror origin
        ignore_axis: Optional[Axis] = None,  # if some axis should be ignored on homologous vertex search
) -> Callable[[MeshVertex, MeshVertex], float]:
    scale0: List[int] = [1, 1, 1]
    scale1: List[int] = [1, 1, 1]
    origin: List[float] = [0, 0, 0]

    scale1[mirror_axis] = -1
    origin[mirror_axis] = mirror_origin

    if ignore_axis is not None:
        scale0[ignore_axis] = 0
        scale1[ignore_axis] = 0

    def get_value(vertex: MeshVertex, axis: Axis, s: List[int]) -> float:
        return (vertex.co[axis] - origin[axis]) * s[axis]

    def computer(a: MeshVertex, b: MeshVertex) -> float:
        x = get_value(a, Axis.X, scale1) - get_value(b, Axis.X, scale0)
        y = get_value(a, Axis.Y, scale1) - get_value(b, Axis.Y, scale0)
        z = get_value(a, Axis.Z, scale1) - get_value(b, Axis.Z, scale0)
        return x * x + y * y + z * z

    return computer


def _invert_uv(uv: List[float], axis: Optional[Axis], origin: float) -> List[float]:
    return uv if axis is None else axis.invert(uv, (origin, origin))


E = TypeVar("E")


def _contains_all(elements: Iterable[E], collection: Container[E]) -> bool:
    for e in elements:
        if e not in collection:
            return False
    return True


def _offset(s: Sequence[E], offset: int) -> List[E]:
    if offset == 0 and isinstance(s, list):
        return s
    return [*s[offset:], *s[0:offset]]


def _flip_name_candidates(name: str) -> List[str]:
    flipped = flip_name(name)
    if flipped != name:
        return [flipped, name]
    else:
        return [name]
