from dataclasses import dataclass
from typing import Optional


@dataclass
class CompilerOptions:
    stdlib_path: str
    stdlib_include: list[str]
    cwd: str
    enable_color: bool


class Globals:
    _compiler_options: Optional[CompilerOptions] = None

    @staticmethod
    def get_compiler_options() -> CompilerOptions:
        if not Globals._compiler_options:
            raise ValueError("compiler options not specified")
        return Globals._compiler_options

    @staticmethod
    def set_compiler_options(opts: CompilerOptions) -> None:
        Globals._compiler_options = opts
