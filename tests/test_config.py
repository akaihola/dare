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


@pytest.mark.skipif(platform.system() != "Linux", reason="Linux-specific test")
def test_config_linux(temp_config_setup, monkeypatch):
    """Test that configuration is read from the correct location on Linux."""
    tmp_path, config_file = temp_config_setup

    # Set HOME environment variable to our temporary directory
    monkeypatch.setenv("HOME", str(tmp_path))
    print(f"\nSet HOME to: {tmp_path}")

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


@pytest.mark.skipif(platform.system() != "Darwin", reason="macOS-specific test")
def test_config_macos(temp_config_setup, monkeypatch):
    """Test that configuration is read from the correct location on macOS."""
    tmp_path, config_file = temp_config_setup

    # Set HOME environment variable to our temporary directory
    monkeypatch.setenv("HOME", str(tmp_path))
    print(f"\nSet HOME to: {tmp_path}")

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


@pytest.mark.skipif(platform.system() != "Windows", reason="Windows-specific test")
def test_config_windows(temp_config_setup, monkeypatch):
    """Test that configuration is read from the correct location on Windows."""
    tmp_path, config_file = temp_config_setup

    # Set USERPROFILE environment variable to our temporary directory
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
