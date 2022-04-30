# anatawa12's model export program
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


from enum import IntEnum
from typing import List, Tuple


class Axis(IntEnum):
    X: int = 0
    Y: int = 1
    Z: int = 2

    def invert(self, vertex: List[float], origin: Tuple[float, ...] = (0, 0, 0)) -> List[float]:
        v = [*vertex]
        v[self] = -(v[self] - origin[self]) + origin[self]
        return v


def vertex_eq(v1: List[float], v2: List[float], limit: float = 0.0001) -> bool:
    if len(v1) != len(v2):
        return False
    for e1, e2 in zip(v1, v2):
        if abs(e1 - e2) > limit:
            return False
    return True
