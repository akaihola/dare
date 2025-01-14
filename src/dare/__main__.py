import dataclasses
import subprocess
import sys
import textwrap
from typing import Iterator, Optional

import click
import llm
import typed_settings as ts
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
    stream: bool = dataclasses.field(
        default=False,
        metadata={"typed-settings": {"help": "Stream the LLM response incrementally"}},
    )


@click.command()
@ts.click_options(Settings, "dare")
@click.argument("prompt_parts", nargs=-1, required=True)
def main(settings: Settings, prompt_parts: tuple[str, ...]):
    """A command line tool to generate Python scripts using LLM.

    Args:
        prompt_parts: The text prompt parts to send to the LLM
        max_tokens: Maximum number of tokens for the LLM response
        show_config: If True, display current configuration and exit
    """
    prompt = " ".join(prompt_parts)

    # Check for piped or redirected input
    if not sys.stdin.isatty():
        piped_input = sys.stdin.read()
        if piped_input:
            prompt += "\n\n" + piped_input
    from dare.prompts import SCRIPT_GENERATION

    system_prompt = textwrap.dedent(SCRIPT_GENERATION)

    # Get the default model
    model = llm.get_model()

    # Show the effective configuration and exit if --show-config is used
    if settings.show_config:
        click.echo(f"Effective configuration: {dataclasses.asdict(settings)}")
        return

    def get_response_stream(model, prompt: str, stream: bool = False) -> Iterator[str]:
        """Helper to get response chunks whether streaming or not."""
        response = model.prompt(prompt, stream=stream, max_tokens=settings.max_tokens)
        if stream:
            yield from response
        else:
            yield response.text()

    # Set up console for output
    console = Console(force_terminal=True)

    response = get_response_stream(
        model, system_prompt + prompt, stream=settings.stream
    )

    # Initialize variables for streaming
    script_name = None
    script_content = []
    in_content = "before"
    buffer = []
    collected_output = []

    for chunk in response:
        buffer.append(chunk)
        # Try to process complete lines
        if "\n" in chunk:
            lines = "".join(buffer).splitlines(True)
            # Keep the last partial line in buffer
            *complete_lines, buffer = lines
            buffer = [buffer]

            for line in complete_lines:
                collected_output.append(line)
                console.print(line, end="")
                if line.startswith('``` py title="') and in_content == "before":
                    script_name = line.split('"')[1]
                    in_content = "script"
                    script_content = []  # Reset script content
                elif line.startswith("```") and in_content == "script":
                    in_content = "after"
                elif in_content == "script":
                    script_content.append(line)

    # Process any remaining content
    if buffer:
        last_line = "".join(buffer)
        collected_output.append(last_line)
        console.print(last_line, end="")
        if in_content == "script" and not last_line.startswith("```"):
            script_content.append(last_line)

    # Print any remaining output
    full_output = "".join(collected_output)
    console.print(full_output)

    script_content = "".join(script_content)  # Changed from join with newlines

    if not script_name:
        raise ValueError("Script name not found in the response")

    if not script_content.strip():
        raise ValueError("Script content is empty or whitespace-only")

    # Write the script to a file
    with open(script_name, "w") as f:
        f.write(script_content)

    if sys.stdin.isatty():
        if not click.confirm("Do you want to run the generated script?"):
            click.echo("Script execution cancelled.")
            return
    else:
        click.echo(
            f"To run the generated script, use the following command:\nuv run {script_name}"
        )
        return

    # Execute the generated script using uv run
    subprocess.run(["uv", "run", script_name])


if __name__ == "__main__":
    main()
