# pyrite

A heavily experimental compiler front-end that uses LLVM to compile a subset of Python source code into standalone executables.

## Usage

Pyrite requires a working distribution of Clang to be installed. For Windows systems, it is sufficient
to use the prebuilt binaries, which can be found [here](https://github.com/llvm/llvm-project/releases) (the installer should have a name that looks like `LLVM-14.0.0-win64.exe`).
To specify an exact Clang path, the `CompilerOptions.clang_command` option can be manually changed in `pyrite.py`. Other compiler options can be in a similar way. The ability
to configure the Pyrite compiler via command line arguments will be implemented at a later date.

Currently, this compiler doesn't produce any binaries; however it will still process any Python files passed to it.
```
$ python pyrite.py [input-file]
```
