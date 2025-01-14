import dataclasses
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
    no_stream: bool = dataclasses.field(
        default=False,
        metadata={"typed-settings": {"help": "Disable streaming of LLM response"}},
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
        model, system_prompt + prompt, stream=not settings.no_stream
    )

    # Process the response and generate script
    from dare.script_processor import ScriptProcessor

    processor = ScriptProcessor(console)
    processor.process_stream(response)
    processor.save_script()
    processor.run_script()


if __name__ == "__main__":
    main()
