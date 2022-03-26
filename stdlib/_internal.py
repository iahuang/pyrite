"""
stdlib/_internal is a special module automatically imported into the global scope
of all other modules in Pyrite. It contains definitions for built-in
classes such as str and list, as well as providing functions such as _malloc
exclusively for other stdlib modules. Importing _internal will have no effect at compile-time,
and may be done simply to include type definitions.

Functions and types prefixed by _ext are implemented by the compiler for stdlib/_internal ONLY
and cannot be used elsewhere.
"""

from __future__ import annotations
from typing import Any
from _compiler_defined import _ext_Pointer, _ext_Char, _ext_get_byte, _ext_abort, _ext_calloc, _ext_malloc, _ext_free, _ext_to_ptr, _ext_cos

# The functions listed here are only included for standard library modules
__PRAGMA_INTERNAL = ["_malloc", "_calloc"]

""" libc bindings """

def _malloc(size: int) -> _ext_Pointer:
    ptr = _ext_malloc(_ext_to_ptr(size))

    if ptr == 0:
        _ext_abort()

    return ptr


def _calloc(size: int) -> _ext_Pointer:
    ptr = _ext_calloc(_ext_to_ptr(size))

    if ptr == 0:
        _ext_abort()

    return ptr

def _math_cos(x: float) -> float:
    return _ext_cos(x)

""" Built-in types """

class str:
    __ptr: _ext_Pointer
    __length: int

    def __new(self, c_str: _ext_Pointer):
        length = 0

        c = _ext_get_byte(c_str)

        while c != 0:
            length += 1
            c_str += 1

            c = _ext_get_byte(c_str)

        self.__ptr = _malloc(length)
        self.__length = length

    def __len__(self) -> int:
        return self.__length

    def __destructor(self) -> None:
        _ext_free(self.__ptr)
