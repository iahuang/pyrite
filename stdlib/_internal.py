from __future__ import annotations
from typing import Any

# should be made inaccessible by the compiler
__PRAGMA_MODULE_PRIVATE = ["__Pointer", "_to_ptr", "__Char", "_malloc", "_calloc"]

""" internal functions - to be resolved at compile-time for this library only  """

def _to_ptr(size: int) -> __Pointer:
    raise NotImplementedError()

def _to_char(b: int) -> __Char:
    raise NotImplementedError()

def _get_byte(ptr: __Pointer) -> __Char:
    raise NotImplementedError()

def _set_byte(ptr: __Pointer, val: __Char) -> __Char:
    raise NotImplementedError()

class __Struct:
    pass

""" c types - to be resolved at compile-time for this library only """

class __Pointer:
    """ platform-dependent data size, usually 64 bits. internally, i8* in LLVM """

    def __add__(self, offset: Any) -> __Pointer:
        raise NotImplementedError()
    
    def __sub__(self, offset: Any) -> __Pointer:
        raise NotImplementedError()

class __Char:
    """ a representation of a single byte """
    
    def __add__(self, offset: Any) -> __Char:
        raise NotImplementedError()
    
    def __sub__(self, offset: Any) -> __Char:
        raise NotImplementedError()

""" libc functions - to be linked at compile-time for this library only """

def __extern_malloc(size: __Pointer) -> __Pointer:
    raise NotImplementedError()

def __extern_calloc(size: __Pointer) -> __Pointer:
    raise NotImplementedError()

def __extern_free(ptr: __Pointer) -> None:
    raise NotImplementedError()

def __extern_abort() -> None:
    raise NotImplementedError()

""" libc bindings """

def _malloc(size: int) -> __Pointer:
    ptr = __extern_malloc(_to_ptr(size))
    
    if ptr == 0:
        __extern_abort()
    
    return ptr

def _calloc(size: int) -> __Pointer:
    ptr = __extern_calloc(_to_ptr(size))
    
    if ptr == 0:
        __extern_abort()
    
    return ptr

class __str(__Struct):
    __ptr: __Pointer
    __length: int

    def __new(self, c_str: __Pointer):
        length = 0

        c = _get_byte(c_str)

        while c != 0:
            length += 1
            c_str += 1

            c = _get_byte(c_str)
        
        self.__ptr = _malloc(length - 1)
        self.__length = length - 1
    
    def __len__(self) -> int:
        return self.__length

    def __destructor(self) -> None:
        __extern_free(self.__ptr)
