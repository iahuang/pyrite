from typing import Optional, TypeVar

def with_unix_endl(string: str) -> str:
    """Return [string] with UNIX-style line endings"""

    return string.replace("\r\n", "\n").replace("\r", "")

T = TypeVar("T")


def unwrap(v: Optional[T]) -> T:
    """
    Unrwap an optional value. Raise a ValueError if the value is None.
    """
    
    if v is not None:
        return v
    raise ValueError("attempted to unwrap None value")
