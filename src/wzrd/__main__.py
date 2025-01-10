import subprocess
import textwrap
import llm
import click
import tomllib
import os


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
    """A command line tool to generate Python scripts using LLM"""
    prompt = " ".join(prompt)

    # System prompt for the LLM
    system_prompt = textwrap.dedent("""
    You write Python tools as single files.

    These files can include dependencies on libraries such as Click.
    If they do, those dependencies are included in a PEP 723 dependencies list.
    The script is enclosed in a Markdown code block with on its opening line
    the `py` language identifier
    and the script name enclosed in `title="<script name>"`.

    Here is an example response:

    <example response>
    This is a leading paragraph which starts your response. The script follows.

    ``` py title="click_example.py"
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

    # Read configuration from wzrd.toml
    config_path = os.path.join(os.path.expanduser("~"), ".config", "wzrd", "wzrd.toml")
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
    script = response.text()

    # Extract script name and content
    script_name = None
    script_content = []
    in_content = False
    for line in script.splitlines():
        if line.startswith('``` py title="'):
            script_name = line.split('"')[1]
            in_content = True
        elif line.startswith("```"):
            in_content = not in_content
        elif in_content:
            script_content.append(line)
    script_content = "\n".join(script_content)

    click.echo_via_pager(script)

    if not script_name:
        raise ValueError("Script name not found in the response")

    if not script_content.strip():
        raise ValueError("Script content is empty or whitespace-only")
    click.echo_via_pager(script)

    # Write the script to a file
    with open(script_name, "w") as f:
        f.write(script_content)

    # Run the script using uvx
    # Run the script using uv run
    subprocess.run(["uv", "run", script_name])


if __name__ == "__main__":
    main()
