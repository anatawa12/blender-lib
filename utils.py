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
from typing import List, Tuple, Union
import bpy


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


# Clone of BLI_string_flip_side_name
# This will be exposed to python since 3.1.0 as `bpy.utils.flip_name`.
# When This script is ported to blender 3.1.x, use it.
if bpy.app.version[0] >= 3 and bpy.app.version[1] >= 1:  # type: ignore
    flip_name = bpy.utils.flip_name  # type: ignore
else:
    def _is_char_sep(sep: str) -> bool:
        return sep in ". -_"


    def flip_name(name: str, strip_digits: bool = False) -> str:
        _lrLR_mapping = {'l': 'r', 'r': 'l', 'L': 'R', 'R': 'L'}

        number = ""

        if len(name) < 3:
            return name

        # .### suffix
        if name[len(name) - 1].isdigit():
            index = name.find('.')
            if index >= 0 and name[index + 1].isdigit():
                if not strip_digits:
                    number = name[index:]
                name = name[:index]

        # <sep>[rRlL] suffix
        if len(name) >= 2 and _is_char_sep(name[len(name) - 2]):
            found = _lrLR_mapping.get(name[len(name) - 1])
            if found is not None:
                return f"{name[:len(name) - 1]}{found}{number}"

        # if starting with [rRlL]<sep>
        if len(name) > 1 and _is_char_sep(name[1]):
            found = _lrLR_mapping.get(name[0])
            if found is not None:
                return f"{found}{name[1:]}{number}"

        # if ends/starts with right/left
        if len(name) > 5:
            name_lower = name.lower()

            def _starts_ends(lower: str, find: str) -> Union[int, None]:
                if lower.startswith(find):
                    return 0
                elif lower.endswith(find):
                    return len(lower) - len(find)
                else:
                    return None

            idx = _starts_ends(name_lower, "right")

            if idx is not None:
                if name[idx] == 'r':
                    replace = 'left'
                elif name[idx + 1] == 'i':
                    replace = 'Left'
                else:
                    replace = "LEFT"
                return f"{name[:idx]}{replace}{name[idx+5:]}{number}"

            idx = _starts_ends(name_lower, "left")

            if idx is not None:
                if name[idx] == 'l':
                    replace = 'right'
                elif name[idx + 1] == 'e':
                    replace = 'Right'
                else:
                    replace = "RIGHT"
                return f"{name[:idx]}{replace}{name[idx+4:]}{number}"

        return f"{name}{number}"
