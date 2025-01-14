import dataclasses
import subprocess
import sys
import textwrap
from typing import Any, Iterator, Optional, cast

import click
import llm
from typed_settings import click_options
from rich.console import Console


@dataclasses.dataclass
class Settings:
    max_tokens: Optional[int] = dataclasses.field(
        default=None,
        metadata={
            "typed-settings": {"help": "Maximum number of tokens for the LLM response"}
        },
    )
    show_config: bool = dataclasses.field(
        default=False,
        metadata={
            "typed-settings": {"help": "Show the effective configuration and exit"}
        },
    )
    no_stream: bool = dataclasses.field(
        default=False,
        metadata={
            "typed-settings": {"help": "Disable streaming of LLM response"}
        },
    )
    fix: Optional[str] = dataclasses.field(
        default=None,
        metadata={
            "typed-settings": {"help": "Fix errors in Python script (format: <PY_FILEPATH [ARGS...]>)"}
        },
    )


def read_file(filepath: str) -> str:
    """Read contents of a Python file."""
    with open(filepath, "r") as f:
        return f.read()


def run_script_and_capture_error(cmd: str) -> tuple[bool, str]:
    """Run a Python script and capture any error output."""
    try:
        subprocess.run(cmd.split(), check=True, capture_output=True, text=True)
        return True, ""
    except subprocess.CalledProcessError as e:
        return False, e.stderr


@click.command()
@click_options(Settings, "dare")
@click.argument("prompt_parts", nargs=-1, required=False)
def main(settings: Settings, prompt_parts: tuple[str, ...]) -> None:
    """A command line tool to generate Python scripts using LLM.

    Args:
        prompt_parts: The text prompt parts to send to the LLM
        max_tokens: Maximum number of tokens for the LLM response
        show_config: If True, display current configuration and exit
    """
    # Handle fix mode if --fix option is provided
    if settings.fix:
        cmd_parts = settings.fix.split()
        script_path = cmd_parts[0]
        script_content = read_file(script_path)
        cmd = f"uv run {settings.fix}"

        success, error = run_script_and_capture_error(cmd)
        if success:
            click.echo("Script ran successfully, no fixes needed.")
            return

        prompt = f"Error running {script_path}:\n\n{error}\n\nScript contents:\n\n{script_content}"
        from dare.prompts import SCRIPT_FIX

        system_prompt = textwrap.dedent(SCRIPT_FIX)
    else:
        prompt = " ".join(prompt_parts)
        from dare.prompts import SCRIPT_GENERATION

        system_prompt = textwrap.dedent(SCRIPT_GENERATION)

        # Check for piped or redirected input
        if not sys.stdin.isatty():
            piped_input = sys.stdin.read()
            if piped_input:
                prompt += "\n\n" + piped_input
    # system_prompt is already set above

    # Get the default model
    model = llm.get_model()

    # Show the effective configuration and exit if --show-config is used
    if settings.show_config:
        click.echo(f"Effective configuration: {dataclasses.asdict(settings)}")
        return

    def get_response_stream(model: Any, prompt: str, stream: bool = False) -> Iterator[str]:
        """Helper to get response chunks whether streaming or not."""
        response = model.prompt(prompt, stream=stream, max_tokens=settings.max_tokens)
        if stream:
            yield from response
        else:
            yield response.text()

    # Set up console for output
    console = Console(force_terminal=True)

    response = cast(Iterator[str], get_response_stream(
        model, system_prompt + prompt, stream=not settings.no_stream
    ))

    # Process the response and generate script
    from dare.script_processor import ScriptProcessor

    processor = ScriptProcessor(console)
    processor.process_stream(response)
    processor.save_script()
    processor.run_script()


if __name__ == "__main__":
    main()
