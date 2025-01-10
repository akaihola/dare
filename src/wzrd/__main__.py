import sys
import subprocess
import textwrap
import pydoc
from llm import LLM

def main():
    # Join all command line arguments into a prompt
    prompt = " ".join(sys.argv[1:])
    
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

    # Create an instance of the LLM
    llm = LLM()

    # Generate the script using the LLM
    script = llm.generate(system_prompt + prompt)

    # Page the script for user confirmation
    pydoc.pager(script)

    # Run the script using uvx
    subprocess.run(["uvx", "-c", script])

if __name__ == "__main__":
    main()
