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

from typing import List, cast

import bpy
from bpy.types import Mesh, MeshVertex
from .utils import Axis
from .globals import context


def vertex_eq(v1: List[float], v2: List[float], limit: float = 0.001) -> bool:
    if len(v1) != len(v2):
        return False
    for e1, e2 in zip(v1, v2):
        if abs(e1 - e2) > limit:
            return False
    return True

object = bpy.context.active_object
if not isinstance(object.data, Mesh):
    raise Exception("err")

mesh: Mesh = object.data

axis: Axis = Axis.X
select_both = True

bpy.ops.object.mode_set(context(), mode="OBJECT")

for v1 in cast(List[MeshVertex], mesh.vertices):
    for v2 in cast(List[MeshVertex], mesh.vertices):
        if vertex_eq(v1.co, axis.invert(v2.co)):
            if select_both:
                v1.select = True
                v2.select = True
            elif v1.co[axis] < v2.co[axis]:
                v1.select = True
            else:
                v2.select = True

bpy.ops.object.mode_set(context(), mode="EDIT")
