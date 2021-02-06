from typing import Tuple

import my_typing
from lexer.lexer_classes import (
    BaseConstantMetadataElement, ConstantContext
)
from main_logic_helpers import CommandsSection


class CommandsConstantMetadataElement(BaseConstantMetadataElement):

    @staticmethod
    def get_data_from_constant_context(
            context: ConstantContext) -> Tuple[CommandsSection, ...]:
        return context.commands


class CommandDescriptionsConstantMetadataElement(BaseConstantMetadataElement):

    @staticmethod
    def get_data_from_constant_context(
            context: ConstantContext) -> my_typing.CommandDescriptionsDict:
        return context.command_descriptions
