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
    You write Python tools as single files. They always start with this comment:

    # /// script
    # requires-python = ">=3.12"
    # ///

    These files can include dependencies on libraries such as Click. If they do, those dependencies are included in a list like this one in that same comment (here showing two dependencies):

    # /// script
    # requires-python = ">=3.12"
    # dependencies = [
    #     "click",
    #     "sqlite-utils",
    # ]
    # ///
    """)

    # Get the default model
    model = llm.get_model()

    # Generate the script using the model
    response = model.prompt(system_prompt + prompt, stream=False)
    script = response.text()

    # Page the script for user confirmation
    click.echo_via_pager(script)

    # Run the script using uvx
    subprocess.run(["uvx", script])


if __name__ == "__main__":
    main()
