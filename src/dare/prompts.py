"""System prompts used by the dare tool."""

SCRIPT_GENERATION = """
You write a Python tool as a single .py script file, runnable using `uv run`.

The script can include dependencies on libraries such as Click.
If they do, those dependencies are included in a dependencies list
inside a PEP 723 inline script metadata block.
The script is enclosed in a Markdown code block opened with the language identifier
and the script file name, e.g.
``` py title="my_script.py"

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
"""

SCRIPT_FIX = (
    SCRIPT_GENERATION
    + """
The Python script you previously created has a bug.
Both the script and the error message are attached below.
Think step by step to find the reason for the error.
Think step by step to come up with a solution.
Fix the script and output the corrected version.
"""
)
