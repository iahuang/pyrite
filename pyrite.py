import os
from pathlib import Path
from pyrite.compiler import Compiler
from pyrite.globals import CompilerOptions, Globals
import sys

if __name__ == "__main__":
    Globals.set_compiler_options(CompilerOptions(
        # Look for the stdlib folder in the same directory as the compiler executable
        stdlib_path=Path(__file__).parent.joinpath("stdlib").as_posix(),
        stdlib_include=[],
        cwd=os.getcwd(),
        enable_color=True,
        clang_command="clang"
    ))

    compiler = Compiler()
    compiler.add_source_file(sys.argv[1], True)
    compiler.build()
#     compiler._llvm.compile_ll("""
# ; ModuleID = 'test.c'
# source_filename = "test.c"
# target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
# target triple = "x86_64-pc-windows-msvc19.29.30136"


# @.str = private unnamed_addr constant [10 x i8] c"bruhpenis\\00", align 1

# define dso_local i32 @main() #0  {
#   %1 = alloca i32, align 4
#   store i32 0, i32* %1, align 4
#   %2 = call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([10 x i8], [10 x i8]* @.str, i64 0, i64 0))
#   ret i32 0
# }

# declare dso_local i32 @printf(i8*, ...) #1""", "out.exe")
