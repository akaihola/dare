import subprocess
import textwrap
import llm
import click
import tomllib
import os
import sys
from rich.console import Console
from rich.syntax import Syntax


@click.command()
@click.argument("prompt", nargs=-1)
@click.option(
    "--max-tokens",
    type=int,
    default=None,
    help="Maximum number of tokens for the LLM response",
)
@click.option(
    "--show-config",
    is_flag=True,
    help="Show the effective configuration and exit",
)
def main(prompt, max_tokens, show_config):
    """A command line tool to generate Python scripts using LLM.

    Args:
        prompt: The text prompt to send to the LLM
        max_tokens: Maximum number of tokens for the LLM response
        show_config: If True, display current configuration and exit
    """
    prompt = " ".join(prompt)

    # Check for piped or redirected input
    if not os.isatty(0):
        piped_input = sys.stdin.read()
        if piped_input:
            prompt += "\n\n" + piped_input
    system_prompt = textwrap.dedent("""
    You write a Python tool as a single .py script file, runnable using `uv run`.

    The script can include dependencies on libraries such as Click.
    If they do, those dependencies are included in a dependencies list
    inside a PEP 723 inline script metadata block.
    The script is enclosed in a Markdown code block opened with the language identifier
    and the script file name, e.g. ``` py title="my_script.py"
    
    The script must not accept any command line arguments.
    If the script needs assets, prefer to include the data in the script itself
    and write it to a file if necessary.
    Only as a last resort, the script can download URLs which have known to have existed
    for at least five years.
    
    Do not include instructions on how to install dependencies or run the script.

    Here is a complete example response:

    <example response>
    This script echoes text using the Click library.

    ``` py title="echo_using_click.py"
    # /// script
    # requires-python = ">=3.11"
    # dependencies = [
    #     "click",
    # ]
    # ///
    import click
    click.echo("This works.")
    ```
    </example response>
    """)

    # Get the default model
    model = llm.get_model()

    # Read configuration from dare.toml
    config_path = os.path.join(os.path.expanduser("~"), ".config", "dare", "dare.toml")
    if os.path.exists(config_path):
        with open(config_path, "rb") as f:
            config = tomllib.load(f)
        config_max_tokens = config.get("max-tokens")
    else:
        config_max_tokens = None

    # Use CLI argument if provided, otherwise use config file value
    max_tokens = max_tokens or config_max_tokens

    # Show the effective configuration and exit if --show-config is used
    if show_config:
        effective_config = {
            "max_tokens": max_tokens,
        }
        click.echo(f"Effective configuration: {effective_config}")
        return
    response = model.prompt(system_prompt + prompt, stream=False, max_tokens=max_tokens)
    response_text = response.text()

    # Extract script name and content from the markdown-formatted response
    script_name = None
    script_content = []
    in_content = "before"
    for line in response_text.splitlines():
        if line.startswith('``` py title="') and in_content == "before":
            script_name = line.split('"')[1]
            in_content = "script"
        elif line.startswith("```") and in_content == "script":
            in_content = "after"
        elif in_content == "script":
            script_content.append(line)
    script_content = "\n".join(script_content)

    # Page the script content using rich syntax highlighting
    console = Console(force_terminal=True)
    syntax = Syntax(response_text, "markdown", theme="monokai", line_numbers=False)
    with console.pager(styles=True):
        console.print(syntax)
    if not script_name:
        raise ValueError("Script name not found in the response")

    if not script_content.strip():
        raise ValueError("Script content is empty or whitespace-only")

    # Write the script to a file
    with open(script_name, "w") as f:
        f.write(script_content)

    if os.isatty(sys.stdin.fileno()):
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
