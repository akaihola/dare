dare
====

dare is a command line tool that generates Python scripts using a Language Learning Model (LLM). It takes command line arguments as input, constructs a prompt, and uses the LLM to generate a standalone Python script to solve the request.

Features
--------

- Generates Python scripts based on command line prompts
- Uses the `llm` package from `llm.datasette.io`
- Minimal external dependencies

Installation
------------

To install dare, you need to have Python 3.11 or higher. You can install the package using Flit::

    pip install flit
    flit install

Usage
-----

To use dare, simply run the command followed by your prompt::

    dare <your prompt here>

For example::

    dare create a script to read a CSV file and print the contents

Development
-----------

To contribute to the development of dare, follow these steps:

1. Clone the repository::

    git clone <repository-url>
    cd dare

2. Install the dependencies::

    flit install --deps develop

3. Make your changes and run the tests::

    bash run-tests.sh

License
-------

This project is licensed under the MIT License.
