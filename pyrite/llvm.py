import shutil
from pyrite import fs
from pyrite.command_line import run_command
from pyrite.errors import UserError
from pyrite.globals import Globals
from os.path import join

class LLVMInterface:
    _clang_path: str

    def __init__(self):
        self._clang_path = self._get_clang_path()

    def _get_clang_path(self) -> str:
        clang_path = shutil.which(Globals.get_compiler_options().clang_command)

        if not clang_path:
            raise UserError(
                "Pyrite requires clang to be installed, but no such installation was found."
            )
        
        return clang_path
    
    def compile_ll(self, source: str, output_path: str) -> None:
        """
        Compile the contents of [source] as LLVM IR code, outputting a binary
        specified by [output_path]. If any errors arise in compilation,
        raise an error.
        """

        ir_path = join(self.get_build_directory(), "build.ll")

        fs.write_file(
            path=ir_path,
            data=source
        )

        result = run_command([self._clang_path, ir_path, "-o", output_path])
        
        if result.stderr:
            fs.write_file(
                path=join(self.get_build_directory(), "llvm_error.txt"),
                data=result.stderr
            )

            raise UserError(
                "An unexpected error occurred during the compilation process. A detailed report has been written to {}".format(
                    self.get_build_directory()
                )
            )


    def get_build_directory(self) -> str:
        """
        Pyrite uses a temporary working "build" directory to store files needed for LLVM/Clang
        """
        cwd = Globals.get_compiler_options().cwd

        return join(cwd, "_build")
