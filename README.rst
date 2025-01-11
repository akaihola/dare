dare
====

dare is a command line tool that generates Python scripts using a Large Language Model (LLM).
It takes command line arguments as input, constructs a prompt,
and uses the LLM to generate a standalone Python script to solve the request.
After showing the generated script, dare asks if you want to run it.

Features
--------

- Generates Python scripts based on command line prompts
- Uses the ``llm`` package from ``llm.datasette.io``
- Minimal external dependencies

Installation
------------

To install dare, you need to have Python 3.11 or higher.
You can install the package using e.g. ``pip``, ``uv`` or ``pipx``::

    pip install dare
    uv pip install dare
    uv tool install dare
    pipx install dare

Then simply run::

    dare <your prompt here>

Or, you can skip installing and just run it using ``uvx``::

    uvx dare <your prompt here>

Usage
-----

To use dare, simply run the command followed by your prompt::

    dare <your prompt here>

For example::

    dare create a script to read a CSV file and print the contents

Example run
-----------

Here's an example run of dare (redacting part of the long ouput)::

    $ dare search for toots about uv and LLMs \
           after registering the app and logging in \
           using data from environment variables MASTODON_HOSTNAME, MASTODON_USERNAME and MASTODON_PASSWORD

    Here's a Mastodon search script for finding toots about uv and LLMs:

    ``` py title="search_mastodon.py"
    # /// script
    # requires-python = ">=3.11"
    # dependencies = [
    #     "mastodon.py>=1.8.1",
    # ]
    # ///
    import os
    from mastodon import Mastodon

    def create_app(hostname):
        return Mastodon.create_app(
            "uv-llm-search",
            api_base_url=f"https://{hostname}",
            scopes=['read', 'write'],
            website="https://example.com"
        )

    def main():
        hostname = os.environ["MASTODON_HOSTNAME"]
        username = os.environ["MASTODON_USERNAME"]
        password = os.environ["MASTODON_PASSWORD"]

        # Create app and get credentials
        client_id, client_secret = create_app(hostname)

        # Initialize Mastodon
        mastodon = Mastodon(
            client_id=client_id,
            client_secret=client_secret,
            api_base_url=f"https://{hostname}"
        )

        # Login
        mastodon.log_in(
            username,
            password,
            scopes=['read', 'write']
        )

        # Search for toots containing both terms
        results = mastodon.search("uv llm", result_type="statuses")

        # Print results
        for status in results['statuses']:
            print("-" * 60)
            print(f"From @{status['account']['username']}")
            print(f"Date: {status['created_at']}")
            print(status['content'].replace('</p><p>', '\n\n').replace('<p>', '').replace('</p>', ''))
            print(f"URL: {status['url']}")

    if __name__ == "__main__":
        main()
    ```
    Do you want to run the generated script? [y/N]: y
    Reading inline script metadata from `search_mastodon.py`
    ------------------------------------------------------------
    From @gergely
    Date: 2024-11-09 09:50:20+00:00
    <strong>Adventures into Code Age with an LLM</strong>

    It’s a relaxed Saturday afternoon, and I just remembered some nerdy plots I’ve seen online for various projects [...]

    <a rel="nofollow noopener noreferrer" class="hashtag u-tag u-category" href="https://gergely.imreh.net/blog/tag/claude/" target="_blank">#Claude</a> <a rel="nofollow noopener noreferrer" class="hashtag u-tag u-category" href="https://gergely.imreh.net/blog/tag/llm/" target="_blank">#llm</a> <a rel="nofollow noopener noreferrer" class="hashtag u-tag u-category" href="https://gergely.imreh.net/blog/tag/python/" target="_blank">#python</a>
    URL: https://gergely.imreh.net/blog/2024/11/adventures-into-code-age-with-an-llm/
    ------------------------------------------------------------
    From @simon
    Date: 2024-09-29 21:52:41+00:00
    Here's a recipe for running the Qwen2-VL vision LLM models on Apple Silicon using Python and the mlx-vlm library, via a uv shell one-liner

    Full details on my blog: <a href="https://simonwillison.net/2024/Sep/29/mlx-vlm/" rel="nofollow noopener noreferrer" translate="no" target="_blank"><span class="invisible">https://</span><span class="ellipsis">simonwillison.net/2024/Sep/29/</span><span class="invisible">mlx-vlm/</span></a> - and here's the full output from that example prompt <a href="https://gist.github.com/simonw/9e02d425cacb902260ec1307e0671e17" rel="nofollow noopener noreferrer" translate="no" target="_blank"><span class="invisible">https://</span><span class="ellipsis">gist.github.com/simonw/9e02d42</span><span class="invisible">5cacb902260ec1307e0671e17</span></a>
    URL: https://fedi.simonwillison.net/@simon/113223058177508383


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
