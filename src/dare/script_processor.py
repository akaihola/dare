import re
import subprocess
import sys
from typing import Iterator

import click
from rich.console import Console


class ScriptProcessor:
    def __init__(self, console: Console) -> None:
        self.console = console
        self.script_name: str | None = None
        self.script_content: list[str] = []
        self.in_content: str = "before"
        self.buffer: list[str] = []
        self.collected_output: list[str] = []

    def process_stream(self, response: Iterator[str]) -> None:
        """Process the LLM response stream and extract script content."""
        for chunk in response:
            self.buffer.append(chunk)
            # Try to process complete lines
            if "\n" in chunk:
                lines = "".join(self.buffer).splitlines(True)
                # Keep the last partial line in buffer
                *complete_lines, last_line = lines
                self.buffer = [last_line]

                for line in complete_lines:
                    self.collected_output.append(line)
                    self.console.print(line, end="")
                    match = re.match(r'^```\s?py\s+title="([^"]+)"', line)
                    if match and self.in_content == "before":
                        self.script_name = match.group(1)
                        self.in_content = "script"
                        self.script_content = []
                    elif line.startswith("```") and self.in_content == "script":
                        self.in_content = "after"
                    elif self.in_content == "script":
                        self.script_content.append(line)

        # Process any remaining content
        if self.buffer:
            last_line = "".join(self.buffer)
            self.collected_output.append(last_line)
            self.console.print(last_line, end="")
            if self.in_content == "script" and not last_line.startswith("```"):
                self.script_content.append(last_line)

        # Print any remaining output
        full_output = "".join(self.collected_output)
        self.console.print(full_output)

    def save_script(self) -> None:
        """Save the extracted script to a file."""
        script_content = "".join(self.script_content)

        if not self.script_name:
            raise ValueError("Script name not found in the response")

        if not script_content.strip():
            raise ValueError("Script content is empty or whitespace-only")

        with open(self.script_name, "w") as f:
            f.write(script_content)

    def run_script(self) -> None:
        """Run the generated script if user confirms."""
        if sys.stdin.isatty():
            if not click.confirm("Do you want to run the generated script?"):
                click.echo("Script execution cancelled.")
                return
        else:
            click.echo(
                f"To run the generated script, use the following command:\nuv run {self.script_name}"
            )
            return

        if self.script_name:
            subprocess.run(["uv", "run", self.script_name])
