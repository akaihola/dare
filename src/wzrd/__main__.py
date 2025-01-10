import argparse
import subprocess
import textwrap
import llm
import click


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="A command line tool to generate Python scripts using LLM"
    )
    parser.add_argument(
        "prompt", nargs=argparse.REMAINDER, help="The prompt to generate the script"
    )
    args = parser.parse_args()

    # Join all positional arguments into a prompt
    prompt = " ".join(args.prompt)

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

    # Generate the script using the model
    response = model.prompt(system_prompt + prompt, stream=False)
    script = response.text()

    # Extract script name and content
    script_name = None
    script_content = []
    in_content = False
    for line in script.splitlines():
        if line.startswith('``` py title="'):
            script_name = line.split('"')[1]
        elif line.startswith("```") and in_content:
            in_content = True
        elif line.startswith("```") and in_content:
            in_content = False
        elif in_content:
            script_content.append(line)
    script_content = "\n".join(script_content)

    if not script_name:
        raise ValueError("Script name not found in the response")

    # Page the script for user confirmation
    click.echo_via_pager(script_content)

    # Write the script to a file
    with open(script_name, "w") as f:
        f.write(script_content)

    # Run the script using uvx
    # Run the script using uv
    subprocess.run(["uv", script_name])


if __name__ == "__main__":
    main()
