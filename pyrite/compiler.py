from pathlib import Path
from typing import Optional
from pyrite.console import CompileLogger
from pyrite.errors import CompileError, UserError
from pyrite.globals import CompilerOptions, Globals
from pyrite.llvm import LLVMInterface
from pyrite.module import Module, ModuleSource, ModuleType


class Compiler:
    _modules: list[Module]
    _entry_module: Optional[Module]
    _llvm: LLVMInterface

    def __init__(self):
        self._modules = []
        self._entry_module = None
        self._llvm = LLVMInterface()

    def _register_module(self, source: ModuleSource) -> Module:
        module = Module(source)
        self._modules.append(module)

        return module

    def _stdlib_include(self, module_name: str) -> None:
        self._register_module(ModuleSource(
            type=ModuleType.STDLIB,
            qualifier=module_name
        ))

    def add_source_file(self, path: str, is_main: bool) -> None:
        module = self._register_module(ModuleSource(
            type=ModuleType.SOURCE_FILE,
            qualifier=path
        ))

        if is_main:
            self._entry_module = module

    def build(self) -> None:
        logger = CompileLogger(
            enable_color=Globals.get_compiler_options().enable_color
        )

        for module in self._modules:
            try:
                module.compile()
            except CompileError as err:
                logger.log_compile_error(module, err)
            except UserError as err:
                logger.log_user_error(err)
    
    def get_global_options(self) -> CompilerOptions:
        return Globals.get_compiler_options()