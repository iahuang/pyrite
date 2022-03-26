from typing import Any, Optional
from termcolor import colored
from pyrite.errors import CompileError, SemanticError, UserError
from pyrite.module import Module


class CompileLogger:
    enable_color: bool

    def __init__(self, enable_color: bool):
        self.enable_color = enable_color

    def _colored(self, text: Any, color: Optional[str] = None) -> str:
        if self.enable_color:
            return colored(str(text), color)

        return str(text)

    def _indented(self, text: str, indent: int = 2) -> str:
        return "\n".join(
            (" "*indent) + line
            for line in text.split("\n")
        )

    def log_compile_error(self, module: Module, error: CompileError) -> None:
        print(self._colored(
            'Error in module {}:'.format(
                self._colored(module.get_source_path(), color="cyan"),
            ),
            color="red"
        ))

        if isinstance(error, SemanticError):
            line_no = error.offending_node.lineno

            print(self._colored(self._indented(
                "on line {}: {}\n| {}".format(
                    line_no,
                    error.message,
                    module.get_source().get_line_content(line_no)
                )
            ), color="red"))
        else:
            print(self._colored(self._indented(
                "error: {}".format(
                    error.message
                )
            ), color="red"))
    
    def log_user_error(self, err: UserError):
        print(self._colored(
            "error: "+err.message,
            color="red"
        ))