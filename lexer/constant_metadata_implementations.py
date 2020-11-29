from typing import Tuple, List, Dict, Callable

from lexer.lexer_classes import (
    BaseConstantMetadataElement, ConstantContext, Command
)


class CommandsConstantMetadataElement(BaseConstantMetadataElement):

    @staticmethod
    def get_data_from_constant_context(
            context: ConstantContext) -> Tuple["Command", ...]:
        return context.commands


class CommandDescriptionsConstantMetadataElement(BaseConstantMetadataElement):

    @staticmethod
    def get_data_from_constant_context(
            context: ConstantContext) -> Dict[str, List[Callable]]:
        return context.command_descriptions
