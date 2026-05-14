# tools.py
import shutil
import subprocess
import platform
from pathlib import Path
from typing import Callable, Optional


class AgenticRagTools:
    """
    Toolset for agentic RAG: listing files, grep (ripgrep), and reading file excerpts.
    All operations are restricted to a safe base directory.
    """

    def __init__(
        self,
        notes_dir: Path,
        grep_timeout_seconds: int,
        read_max_lines: int,
        log_callback: Callable[[str], None],
    ):
        self.notes_dir = notes_dir.resolve()
        self.grep_timeout = grep_timeout_seconds
        self.read_max_lines = read_max_lines
        self.log = log_callback

    # --------------------------------------------------------------
    # Internal helpers
    # --------------------------------------------------------------

    def _ripgrep_install_hint(self) -> str:
        system = platform.system()
        if system == "Darwin":
            return "Install with `brew install ripgrep`."
        if system == "Windows":
            return (
                "Install with `winget install BurntSushi.ripgrep.MSVC`, "
                "`choco install ripgrep`, or `scoop install ripgrep`."
            )
        return "Install with your package manager, for example `sudo apt-get install ripgrep`."

    def _safe_path(self, path: str) -> Optional[Path]:
        target = (self.notes_dir / path).resolve()
        if not target.is_relative_to(self.notes_dir):
            return None
        return target

    # --------------------------------------------------------------
    # Public tools (called by the agent)
    # --------------------------------------------------------------

    def grep(self, pattern: str, max_results: int = 30, context: int = 0) -> str:
        self.log(f"Running grep | pattern={pattern} max={max_results} context={context}")

        if max_results < 1:
            return "Error: max_results must be 1 or greater."
        if context < 0:
            return "Error: context must be 0 or greater."
        if not shutil.which("rg"):
            return f"Error: ripgrep ('rg') is not installed. {self._ripgrep_install_hint()}"

        cmd = [
            "rg",
            "--line-number",
            "--no-heading",
            "--ignore-case",
            "--no-config",
            "--sortr=modified",
            "--max-count",
            str(max_results),
            "--glob",
            "*.md",
            *(["--context", str(context)] if context > 0 else []),
            "--",
            pattern,
            ".",
        ]

        try:
            result = subprocess.run(
                cmd,
                cwd=self.notes_dir,
                capture_output=True,
                text=True,
                check=False,
                timeout=self.grep_timeout,
            )
        except subprocess.TimeoutExpired:
            self.log(f"grep timed out for pattern={pattern}")
            return f"Error: grep timed out after {self.grep_timeout}s. Try a more specific pattern."

        if result.returncode == 2:
            return f"Error: invalid pattern {pattern!r}: {result.stderr.strip()}"

        if not result.stdout.strip():
            return f"No matches found for pattern: {pattern}"

        lines = result.stdout.splitlines()
        self.log(f"grep found {len(lines)} lines")

        if len(lines) > max_results:
            lines = lines[:max_results] + [
                f"... truncated to {max_results} matches. Try a more specific pattern."
            ]

        return "\n".join(lines)

    def list_files(self, pattern: str = "*.md") -> str:
        self.log(f"Listing files with pattern={pattern}")

        if not self.notes_dir.exists():
            return f"Error: notes directory not found at {self.notes_dir}"

        try:
            paths = self.notes_dir.glob(pattern)
        except (NotImplementedError, ValueError) as e:
            return f"Error: invalid glob pattern {pattern!r}: {e}"

        matches = sorted(
            str(path.relative_to(self.notes_dir))
            for path in (p.resolve() for p in paths)
            if path.is_file() and path.is_relative_to(self.notes_dir)
        )

        self.log(f"Found {len(matches)} matching files")

        if not matches:
            return f"No files matched pattern: {pattern}"
        return "\n".join(matches)

    def read_file(self, path: str, offset: int = 1, limit: int = 200) -> str:
        self.log(f"Reading file | path={path} offset={offset} limit={limit}")

        safe = self._safe_path(path)
        if safe is None:
            return f"Error: path {path!r} is outside the notes directory."
        if not safe.exists():
            return f"Error: file not found: {path}"
        if not safe.is_file():
            return f"Error: {path} is not a file."
        if offset < 1:
            return "Error: offset must be 1 or greater."
        if limit < 1:
            return "Error: limit must be 1 or greater."
        if limit > self.read_max_lines:
            return f"Error: limit must be {self.read_max_lines} lines or fewer."

        try:
            lines = safe.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            return f"Error: {path} is not UTF-8 text."

        end = min(offset + limit - 1, len(lines))
        excerpt = lines[offset - 1 : end]

        self.log(f"Read {len(excerpt)} lines from {path}")

        if not excerpt:
            return f"No lines found. {path} has {len(lines)} lines."

        return "\n".join(f"{i}: {line}" for i, line in enumerate(excerpt, start=offset))