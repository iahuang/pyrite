import ast


class CompileError(Exception):
    """
    Base class for code errors that arise during the compilation process
    """
    message: str

    def __init__(self, message: str):
        super().__init__()

        self.message = message


class SemanticError(CompileError):
    """
    Class for code errors that have a specific known offending location in the code
    """
    offending_node: ast.AST

    def __init__(self, offending_node: ast.AST, message: str):
        super().__init__(message)
        self.offending_node = offending_node
        self.message = message


class UserError(Exception):
    """
    Base class for errors that are not related to code (e.g. input file is missing)
    """