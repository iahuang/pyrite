"""
The following module contains type definitions for compiler-implemented functions and classes
used by stdlib/_internal, but this module does not represent real code; it is simply
here to prevent IDE errors. This is not a real module, and importing it is
not allowed. 
"""

from __future__ import annotations
from typing import Any

""" internal functions - to be resolved at compile-time for this library only  """

def _ext_to_ptr(size: int) -> _ext_Pointer:
    raise NotImplementedError()

def _to_char(b: int) -> _ext_Char:
    raise NotImplementedError()

def _ext_get_byte(ptr: _ext_Pointer) -> _ext_Char:
    raise NotImplementedError()

def _set_byte(ptr: _ext_Pointer, val: _ext_Char) -> _ext_Char:
    raise NotImplementedError()

class __Struct:
    pass

""" c types - to be resolved at compile-time for this library only """

class _ext_Pointer:
    """ platform-dependent data size, usually 64 bits. internally, i8* in LLVM """

    def __add__(self, offset: Any) -> _ext_Pointer:
        raise NotImplementedError()
    
    def __sub__(self, offset: Any) -> _ext_Pointer:
        raise NotImplementedError()

class _ext_Char:
    """ a representation of a single byte """
    
    def __add__(self, offset: Any) -> _ext_Char:
        raise NotImplementedError()
    
    def __sub__(self, offset: Any) -> _ext_Char:
        raise NotImplementedError()

""" libc functions - to be linked at compile-time for this library only """

def _ext_malloc(size: _ext_Pointer) -> _ext_Pointer:
    raise NotImplementedError()

def _ext_calloc(size: _ext_Pointer) -> _ext_Pointer:
    raise NotImplementedError()

def _ext_free(ptr: _ext_Pointer) -> None:
    raise NotImplementedError()

def _ext_abort() -> None:
    raise NotImplementedError()

def _ext_cos(x: float) -> float:
    raise NotImplementedError()