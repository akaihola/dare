import dataclasses
from typing import Optional


# type: ignore[misc]  # Ignore "Expression type contains Any" errors in this file
@dataclasses.dataclass
class Settings:
    max_tokens: Optional[int] = dataclasses.field(
        default=None,
        metadata={
            "typed-settings": {"help": "Maximum number of tokens for the LLM response"}
        },
    )
    show_config: bool = dataclasses.field(
        default=False,
        metadata={
            "typed-settings": {"help": "Show the effective configuration and exit"}
        },
    )
    no_stream: bool = dataclasses.field(
        default=False,
        metadata={"typed-settings": {"help": "Disable streaming of LLM response"}},
    )
    fix: Optional[str] = dataclasses.field(
        default=None,
        metadata={
            "typed-settings": {
                "help": "Fix errors in Python script (format: <PY_FILEPATH [ARGS...]>)"
            }
        },
    )
