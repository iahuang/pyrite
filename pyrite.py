import os
from pathlib import Path
from pyrite.compiler import Compiler
from pyrite.globals import CompilerOptions, Globals
import sys

if __name__ == "__main__":
    Globals.set_compiler_options(CompilerOptions(
        # Look for the stdlib folder in the same directory as the compiler executable
        stdlib_path=os.path.join(__file__, "stdlib"),
        stdlib_include=[],
        cwd=os.getcwd(),
        enable_color=True
    ))

    compiler = Compiler()
    compiler.add_source_file(sys.argv[1], True)
    compiler.build()