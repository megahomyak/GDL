import re
from dataclasses import dataclass
from typing import Tuple, Callable, Awaitable, Optional, Type

import lexer.exceptions
from handlers.handler_helpers import HandlingResult
from lexer.lexer_classes import (
    ConstantContext, ConvertedCommand, Arg,
    BaseConstantMetadataElement, BaseMetadataElement, Context
)


@dataclass
class Command:
    names: Tuple[str, ...]
    handler: Callable[..., Awaitable[HandlingResult]]
    description: Optional[str] = None
    metadata: Tuple[Type[BaseMetadataElement], ...] = ()
    constant_metadata: Tuple[Type[BaseConstantMetadataElement], ...] = ()
    fillers: tuple = ()
    arguments: Tuple[Arg, ...] = ()

    def convert_command_to_args(
            self, command: str, separator: str = " ") -> ConvertedCommand:
        """
        Takes some str, converts it to tuple with some values.

        Args:
            command:
                user input (like "command arg1 arg2")
            separator:
                what symbol needs to be between arguments (regex); default " "

        Returns:
            tuple of some values, which are converted arguments from string
        """
        for args_num in range(len(self.arguments) + 1):
            names = '|'.join(re.escape(name) for name in self.names)
            pattern = separator.join(
                [
                    f"(?i)({names})", *[
                        f"({arg.type.regex})"
                        for arg in self.arguments[:args_num]
                    ]  # Something like (\d\d)
                ]  # Something like (?i)(command) (\d\d)
            ) + ("$" if args_num == len(self.arguments) else "")
            rgx_result = re.match(pattern, command)
            if rgx_result is None:
                raise lexer.exceptions.ParsingError(args_num)
        # noinspection PyUnboundLocalVariable
        # because range(len(self.arguments) + 1) will be at least with length of
        # 1
        rgx_groups = rgx_result.groups()
        # noinspection PyArgumentList
        # because IDK why it thinks that `arg` argument is already filled
        # (like `self`)
        return ConvertedCommand(
            name=rgx_groups[0],
            arguments=[
                converter(group) for group, converter in zip(
                    rgx_groups[1:], [arg.type.convert for arg in self.arguments]
                )
            ]
        )

    def get_converted_metadata(self, context: Context) -> tuple:
        """
        Takes context, goes through all metadata elements and gets data from
        them using context.

        Args:
            context:
                context, which will be passed to the conversion function of
                every metadata element

        Returns:
            tuple of data received from the metadata elements
        """
        return tuple(
            one_metadata.get_data_from_context(context)
            for one_metadata in self.metadata
        )

    def get_converted_constant_metadata(
            self, constant_context: ConstantContext) -> tuple:
        """
        Takes constant context, goes through all constant metadata elements and
        gets data from them using constant context.

        Args:
            constant_context:
                constant context, which will be passed to the conversion
                function of every constant metadata element

        Returns:
            tuple of data received from the constant metadata elements
        """
        return tuple(
            one_constant_metadata.get_data_from_constant_context(
                constant_context
            ) for one_constant_metadata in self.constant_metadata
        )

    def get_full_description(
            self, include_type_descriptions: bool = False,
            include_heading: bool = False) -> str:
        """
        Makes a full description of the command.

        Args:
            include_type_descriptions:
                include description for type of every argument or not
            include_heading:
                include heading ("Description for command '{your_command}':
                {description}") or not

        Returns:
            generated description
        """
        heading_str = (
            f"Описание команды '{self.names[0]}': {self.description}"
        ) if include_heading else None
        aliases_str = (
            f"Псевдонимы: {', '.join(self.names[1:])}"
        ) if len(self.names) > 1 else None
        args = []
        for argument in self.arguments:
            temp_desc = (
                f" - {argument.description}"
            ) if argument.description is not None else ""
            if argument.type.name == argument.name:
                temp_type_name = (
                    f" ({argument.type.description})" if (
                        include_type_descriptions
                        and argument.type.description is not None
                    ) else ""
                )
            else:
                temp_type_name = (
                    f" ({argument.type.name} - {argument.type.description})"
                    if (
                        include_type_descriptions
                        and argument.type.description is not None
                    ) else f" ({argument.type.name})"
                )
            args.append(
                f"{argument.name}{temp_type_name}{temp_desc}"
            )
        args_str = "Аргументы:\n{}".format("\n".join(args)) if args else None
        return "\n".join(
            filter(
                lambda string: string is not None,
                (heading_str, aliases_str, args_str)
            )
        )

    def get_short_full_description(self) -> str:
        additional_names = ", ".join([
            f"или {name}" for name in self.names[1:]
        ]) if len(self.names) > 1 else ""
        arguments = [f"[{arg.description}]" for arg in self.arguments]
        return " ".join(filter(None, [
            f"/{self.names[0]}", f"({additional_names})", *arguments,
            f" - {self.description}" if self.description else ""
        ]))
