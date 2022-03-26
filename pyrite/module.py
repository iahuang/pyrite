from __future__ import annotations

import ast
from dataclasses import dataclass
from enum import Enum
import os
from pathlib import Path
import random
from typing import Optional, Union
from pyrite.errors import CompileError, SemanticError
from pyrite.globals import Globals
from pyrite.util import unwrap


class Type:
    name: str
    built_in: bool
    parent_module_id: Optional[str]
    size_bytes: int
    id: str

    def __init__(self, name: str, built_in: bool, size_bytes: int, parent_module_id: Optional[str] = None) -> None:
        self.name = name
        self.built_in = built_in
        self.parent_module_id = parent_module_id
        self.size_bytes = size_bytes

        if built_in and parent_module_id is not None:
            raise ValueError(
                "built-in type cannot be associated with a module"
            )

        if self.built_in:
            self.id = self.name
        else:
            assert self.parent_module_id
            self.id = self.parent_module_id + "_" + self.name

    def __eq__(self, other: Type) -> bool:
        return self.id == other.id


class Symbol:
    name: str

    def __init__(self, name: str):
        self.name = name


class Scope:
    module: Module
    parent_scope: Union[Scope, GlobalScope]
    _local_variables: dict[str, LocalVariable]

    def __init__(self, module: Module, parent_scope: Union[Scope, GlobalScope]):
        self.module = module
        self.parent_scope = parent_scope
        self._local_variables = {}

    def resolve_symbol(self, identifier: ast.Name) -> Symbol:
        symbol_name = identifier.id

        if symbol_name in self._local_variables:
            return self._local_variables[symbol_name]

        return self.parent_scope.resolve_symbol(identifier)


class FunctionScope(Scope):
    function: TopLevelFunction

    def __init__(self, module: Module, function: TopLevelFunction):
        super().__init__(module=module, parent_scope=module.get_global_scope())
        self.function = function

    def resolve_symbol(self, identifier: ast.Name) -> Symbol:
        args = self.function.get_arguments()

        if identifier.id in args:
            return args[identifier.id]

        return super().resolve_symbol(identifier)


class Variable(Symbol):
    type: Type

    def __init__(self, name: str, type: Type):
        super().__init__(name)
        self.type = type


class LocalVariable(Variable):
    scope: Scope
    function: TopLevelFunction

    def __init__(self, name: str, type: Type, function: TopLevelFunction, scope: Scope):
        super().__init__(name, type)
        self.function = function
        self.scope = scope


class GlobalVariable(Variable):
    scope: GlobalScope

    def __init__(self, name: str, type: Type):
        super().__init__(name, type)


class TopLevelFunction(Symbol):
    return_type: Type
    _function_scope: FunctionScope
    _args: dict[str, LocalVariable]

    def __init__(self, module: Module, name: str, return_type: Type):
        super().__init__(name)

        self.return_type = return_type
        self._function_scope = FunctionScope(module, function=self)

    def add_argument(self, name: str, type: Type):
        if name in self._args:
            raise CompileError("Duplicate argument {}".format(repr(name)))

        self._args[name] = LocalVariable(
            name=name,
            type=type,
            function=self,
            scope=self._function_scope
        )

    def get_arguments(self) -> dict[str, LocalVariable]:
        return self._args


class GlobalScope:
    module: Module
    _tl_functions: list[TopLevelFunction]
    _global_variables: dict[str, GlobalVariable]

    def __init__(self, module: Module):
        self.module = module
        self._tl_functions = []
        self._global_variables = {}

    def resolve_symbol(self, identifier: ast.Name) -> Symbol:
        symbol_name = identifier.id

        if symbol_name in self._global_variables:
            return self._global_variables[symbol_name]

        for function in self._tl_functions:
            if function.name == symbol_name:
                return function

        raise SemanticError(
            identifier, "Unresolved symbol {}".format(repr(symbol_name))
        )


class ModuleType(Enum):
    SOURCE_FILE = 1
    STDLIB = 2
    SOURCE_STRING = 3


class ModuleSource:
    _qualifier: str
    type: ModuleType

    def __init__(self, type: ModuleType, qualifier: str):
        """
        The qualifier argument specifies the "source" of the ModuleSource object:
          - If the module type is STDLIB, then the qualifier should be a module name such as
            "math"
          - If the module type is SOURCE_FILE, then the qualifier should be a file path relative
            to the compiler CWD or an absolute path
          - If the module type is SOURCE_STRING, then the qualifier is simply a code string.
        """
        self.type = type
        self._qualifier = qualifier

    def _resolve_source_file_path(self, path: str) -> str:
        if os.path.isabs(path):
            return path
        opts = Globals.get_compiler_options()
        return Path(opts.cwd, path).as_posix()

    def _resolve_stdlib_file_path(self, name: str) -> str:
        opts = Globals.get_compiler_options()
        return Path(opts.stdlib_path, name, extension=".py").as_posix()

    def get_source_path(self) -> str:
        """
        Return the full path corresponding to this module's source.
        If the source is a string, then throw an error.
        """

        if self.type == ModuleType.SOURCE_FILE:
            return self._resolve_source_file_path(self._qualifier)
        if self.type == ModuleType.STDLIB:
            return self._resolve_stdlib_file_path(self._qualifier)

        raise ValueError("cannot get module path for non-file module")

    def load_source_string(self) -> str:
        """
        Return the source code contents of this module as a string.
        """
        opts = Globals.get_compiler_options()

        if self.type == ModuleType.SOURCE_STRING:
            return self._qualifier

        with open(self.get_source_path()) as fl:
            return fl.read()

    def get_qualifier(self) -> str:
        return self._qualifier

    def make_module_id(self) -> str:
        if self.type == ModuleType.SOURCE_STRING:
            return "src_{:02X}".format(hash(random.random()))

        if self.type == ModuleType.SOURCE_FILE:
            return "mod_{:02X}".format(hash(self.get_qualifier()))

        if self.type == ModuleType.STDLIB:
            return "lib_{:02X}".format(hash(self.get_qualifier()))

        raise ValueError()

    def get_source_directory(self) -> str:
        """
        Return the directory containing this source file; if the source
        file is a source string, then return the compiler CWD
        """
        if self.type == ModuleType.SOURCE_STRING:
            return Globals.get_compiler_options().cwd

        abs_path = ""

        if self.type == ModuleType.SOURCE_FILE:
            abs_path = self._resolve_source_file_path(self._qualifier)

        if self.type == ModuleType.STDLIB:
            abs_path = self._resolve_stdlib_file_path(self._qualifier)

        return Path(abs_path).parent.as_posix()

    def get_line_content(self, lineno: int) -> str:
        """
        Return the contents of line [lineno] of the source code, where [lineno] starts at 1.
        """

        return self.load_source_string().split("\n")[lineno - 1]


def load_internal_module() -> Module:
    """
    stdlib/_internal defines a collection of types and methods that are meant to be
    built in to the Python runtime, such as "str" and "list".

    _internal should not be registered as an actual module dependency, but its contents
    should be compiled independently and placed at the top of every built LLVM file.
    """

    internal = Module(ModuleSource(ModuleType.STDLIB, "_internal"))
    internal.compile()
    return internal


@dataclass
class ModulePragma:
    private_symbols: list[str]
    use_extern: bool


class Module:
    _module_type: ModuleType
    _source: ModuleSource
    _source_code_cache: str
    _root_node: Optional[ast.Module]

    id: str

    # Semantics
    _types: dict[str, Type]
    _global_scope: GlobalScope

    def __init__(self, source: ModuleSource):
        self._source = source
        self._module_type = source.type
        self._source_code_cache = ""
        self._types = {}

        self.id = source.make_module_id()
        self._global_scope = GlobalScope(module=self)

    def _load_builtin_types(self) -> None:
        builtin = [
            Type("int", size_bytes=4, built_in=True),
            Type("str", size_bytes=8, built_in=True),
            Type("bool", size_bytes=1, built_in=True),
            Type("float", size_bytes=4, built_in=True),
            Type("None", size_bytes=0, built_in=True)
        ]

        # load _internal module

        internal = load_internal_module()

        for type in internal.get_types():
            self._register_type(type)

        for type in builtin:
            self._register_type(type)

    def _register_type(self, type: Type) -> None:
        self._types[type.name] = type

    def _load_and_build_ast(self) -> None:
        self._source_code_cache = self._source.load_source_string()
        self._root_node = ast.parse(self._source_code_cache)

    def get_dependencies(self) -> list[str]:
        dependencies: list[str] = []

        for node in self.assert_ast_loaded().body:
            if isinstance(node, ast.Import):
                dependencies.extend(
                    module.name
                    for module in node.names
                )

        return dependencies

    def _resolve_type_name(self, name: str) -> Optional[Type]:
        return self._types.get(name)

    def resolve_type(self, identifier: ast.expr) -> Type:
        type_name = None

        if isinstance(identifier, ast.Constant):
            type_name = str(identifier.value)
        if isinstance(identifier, ast.Name):
            type_name = str(identifier.id)

        if type_name is None:
            raise SemanticError(identifier, "Invalid return type expression")

        type = self._resolve_type_name(type_name)

        if not type:
            raise SemanticError(
                identifier, "Unknown type {}".format(repr(type_name)))

        return type

    def _handle_top_level_function(self, fdef_node: ast.FunctionDef) -> TopLevelFunction:
        """
        Parse out information about a top-level function
        """

        body = fdef_node.body

        # check that function return signature exists
        return_type_expr = fdef_node.returns
        if return_type_expr is None:
            raise SemanticError(fdef_node, "Function is missing return type")

        function = TopLevelFunction(
            module=self,
            name=fdef_node.name,
            return_type=self.resolve_type(return_type_expr)
        )

        for node in body:
            pass

        return function

    def _resolve_pragmas(self) -> None:
        """
        Some modules may have top-level constants prefixed with "__PRAGMA", as a way to provide
        additional information to the compiler. Only stdlib modules are currently allowed to
        use pragmas.

        This method should be called pre-compilation, and will scan the module for these
        directives and parse out information.
        """

        for node in self.assert_ast_loaded().body:
            # TODO: implement
            pass

    def compile(self) -> None:
        self._load_and_build_ast()
        self._load_builtin_types()

        for node in unwrap(self._root_node).body:
            if isinstance(node, ast.FunctionDef):
                self._handle_top_level_function(node)

    def get_global_scope(self) -> GlobalScope:
        return self._global_scope

    def get_source_path(self) -> str:
        return self._source.get_source_path()

    def get_source(self) -> ModuleSource:
        return self._source

    def get_types(self) -> list[Type]:
        return list(self._types.values())

    def assert_ast_loaded(self) -> ast.Module:
        """
        The actual source code contents of a module are not actually read until
        the _load_and_build_ast method is called. This method will ensure that
        this method has been called, and if so, return the corresponding AST root
        """

        if self._root_node:
            return self._root_node

        raise ValueError()

    def is_internal_module(self) -> bool:
        """
        The module stdlib/_internal has special properties, as it interacts directly with
        LLVM and libc, and therefore has additional methods and types.

        Return True if this module is stdlib/_internal
        """

        return self._source.type == ModuleType.STDLIB and self._source.get_qualifier() == "_internal"
