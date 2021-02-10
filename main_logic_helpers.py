import typing
from dataclasses import dataclass
from typing import Tuple

if typing.TYPE_CHECKING:
    from lexer.lexer_classes import Command


@dataclass
class CommandsSection:
    name: str
    commands: Tuple["Command", ...]

    def get_compact_command_descriptions(
            self, add_dot_before_name: bool = False) -> str:
        descriptions = '\n'.join(f'{num}. {desc}' for num, desc in enumerate(
            (command.get_short_full_description() for command in self.commands),
            start=1
        ))
        return (
            f"{'• ' if add_dot_before_name else ''}{self.name}:\n{descriptions}"
        )
