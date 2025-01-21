import dataclasses
from typing import Optional


def mkhelp(help_text: str) -> dict[str, dict[str, str]]:
    return {"typed-settings": {"help": help_text}}


@dataclasses.dataclass
class Settings:
    max_tokens: Optional[int] = dataclasses.field(
        default=None,
        metadata=mkhelp("Maximum number of tokens for the LLM response"),
    )
    show_config: bool = dataclasses.field(
        default=False,
        metadata=mkhelp("Show the effective configuration and exit"),
    )
    no_stream: bool = dataclasses.field(
        default=False,
        metadata=mkhelp("Disable streaming of LLM response"),
    )
    fix: Optional[str] = dataclasses.field(
        default=None,
        metadata=mkhelp("Fix errors in Python script (format: <PY_FILEPATH [ARGS...]>)"),
    )
    model: Optional[str] = dataclasses.field(
        default=None,
        metadata=mkhelp("Name of the LLM model to use"),
    )
