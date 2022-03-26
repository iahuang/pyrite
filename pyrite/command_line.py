from dataclasses import dataclass
import subprocess
import pyrite.util as util
import shutil


@dataclass
class CommandOutput:
    stdout: str
    stderr: str


def run_command(args: list[str]) -> CommandOutput:
    """Run a command, returning the output of the child process"""

    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    stdout, stderr = p.communicate()

    stdout = util.with_unix_endl(stdout.decode("utf8"))
    stderr = util.with_unix_endl(stderr.decode("utf8"))

    return CommandOutput(stdout, stderr)
