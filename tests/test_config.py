import ast
import importlib
import os
import platform
from textwrap import dedent

import pytest
from click.testing import CliRunner
from platformdirs import user_config_path

import dare.__main__


@pytest.fixture
def config_content():
    """Fixture that returns a sample configuration content."""
    return dedent(
        """
        [dare]
        # Sample configuration for testing
        max_tokens = 1000
        no_stream = true
        model = "test-model"
        """
    )


@pytest.fixture
def temp_config_setup(tmp_path, config_content):
    """Set up a temporary configuration directory and file."""
    # Create the dare directory in the temp path
    config_dir = tmp_path / "dare"
    config_dir.mkdir(exist_ok=True)

    # Create the configuration file
    config_file = config_dir / "dare.toml"
    config_file.write_text(config_content)

    # Print debug information
    print(f"\nTemporary config file created at: {config_file}")
    print(f"Config content:\n{config_content}")

    return tmp_path, config_file


def parse_config_output(output):
    """Parse the configuration dictionary from the output string."""
    # Print the raw output for debugging
    print(f"\nRaw output: {output}")

    # Extract the dictionary part from the output
    start_idx = output.find("{")
    end_idx = output.rfind("}")
    if start_idx == -1 or end_idx == -1:
        raise ValueError(f"Could not find dictionary in output: {output}")

    dict_str = output[start_idx : end_idx + 1]
    # Print the extracted dictionary string for debugging
    print(f"Extracted dict string: {dict_str}")

    # Parse the dictionary string into an actual dictionary
    return ast.literal_eval(dict_str)


@pytest.fixture
def platform_config(request, tmp_path, monkeypatch):
    """Platform-specific configuration fixture."""
    platform_name = request.param

    if platform_name == "Linux":
        # Linux setup
        monkeypatch.setenv("HOME", str(tmp_path))
        print(f"\nSet HOME to: {tmp_path}")
    elif platform_name == "Darwin":
        # macOS setup
        monkeypatch.setenv("HOME", str(tmp_path))
        print(f"\nSet HOME to: {tmp_path}")
    elif platform_name == "Windows":
        # Windows setup
        monkeypatch.setenv("USERPROFILE", str(tmp_path))
        print(f"\nSet USERPROFILE to: {tmp_path}")

        # Also set APPDATA for completeness
        appdata_dir = tmp_path / "AppData" / "Roaming"
        appdata_dir.mkdir(parents=True, exist_ok=True)
        monkeypatch.setenv("APPDATA", str(appdata_dir))
        print(f"Set APPDATA to: {appdata_dir}")

        # Also set LOCAL_APPDATA for completeness
        local_appdata_dir = tmp_path / "AppData" / "Local"
        local_appdata_dir.mkdir(parents=True, exist_ok=True)
        monkeypatch.setenv("LOCAL_APPDATA", str(local_appdata_dir))
        print(f"Set LOCAL_APPDATA to: {local_appdata_dir}")

    return {"platform_name": platform_name, "tmp_path": tmp_path}


@pytest.mark.parametrize(
    "platform_config",
    [
        pytest.param("Linux", id="linux"),
        pytest.param("Darwin", id="macos"),
        pytest.param("Windows", id="windows"),
    ],
    indirect=True,
)
def test_config_platform(platform_config, temp_config_setup):
    """Test that configuration is read from the correct location on different platforms."""
    platform_name = platform_config["platform_name"]

    # Skip if not running on the specified platform
    if platform.system() != platform_name:
        pytest.skip(f"Test only runs on {platform_name}")

    _, config_file = temp_config_setup

    # Get the config path that will be used by platformdirs
    config_dir = user_config_path("dare", appauthor=False)
    print(f"Config directory: {config_dir}")

    # Create the expected config directory structure
    os.makedirs(config_dir, exist_ok=True)

    # Create the configuration file in the expected location
    expected_config_file = config_dir / "dare.toml"
    with open(config_file, "r") as src, open(expected_config_file, "w") as dst:
        dst.write(src.read())

    print(f"Created config file at: {expected_config_file}")

    importlib.reload(dare.__main__)

    # Run the command with --show-config
    runner = CliRunner()
    result = runner.invoke(dare.__main__.main, ["--show-config"])

    # Check that the command succeeded
    assert result.exit_code == 0

    # Parse the configuration dictionary from the output
    config_dict = parse_config_output(result.output)

    # Check that the output contains our configuration values
    assert config_dict["max_tokens"] == 1000
    assert config_dict["no_stream"] is True
    assert config_dict["model"] == "test-model"
