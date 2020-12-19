import datetime
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Any, Tuple, Callable, Dict, List

import lexer.exceptions
from lexer.enums import GrammaticalCases
from main_logic_helpers import CommandsSection


class BaseArgType(ABC):
    """
    Interface for type of argument, does conversion from string to some type.

    It isn't static because quite often it has __init__, where you can specify
    some things, which affects the conversion and regex.
    """

    @property
    def name(self) -> str:
        """
        Shortcut for the self.get_name()

        Returns:
            name of the argument
        """
        return self.get_name()

    @abstractmethod
    def _get_name(
            self, case: GrammaticalCases = GrammaticalCases.NOMINATIVE,
            singular: bool = True) -> Optional[str]:
        """
        Returns the string with the name of the argument or None, if there is
        no matching name. Shouldn't be used, because there is a get_name method,
        which is a wrapper around this method.

        Args:
            case:
                grammatical case of the name
            singular:
                if True, name will be returned in a singular form, else in a
                plural form

        Returns:
            name or None
        """
        pass

    def get_name(
            self, case: GrammaticalCases = GrammaticalCases.NOMINATIVE,
            singular: bool = True) -> str:
        """
        Returns the name of the argument. If nothing found, raises a
        NotImplementedError.

        Args:
            case:
                grammatical case of the name
            singular:
                if True, name will be returned in a singular form, else in a
                plural form

        Returns:
            name of the argument

        Raises:
            NotImplementedError:
                if name in the specified case and form isn't found
        """
        name = self._get_name(case, singular)
        if name is None:
            raise lexer.exceptions.NameCaseNotFound(
                f"There is no {case} for the name of {self.__class__.__name__}!"
            )
        return name

    @property
    @abstractmethod
    def regex(self) -> str:
        pass

    @property
    def description(self) -> Optional[str]:
        return None

    @abstractmethod
    def convert(self, arg: str) -> Any:
        """
        Converts incoming argument to some type

        Args:
            arg: str with some argument

        Returns:
            arg converted to some type
        """
        pass


@dataclass
class Arg:
    name: str
    type: BaseArgType
    description: Optional[str] = None


@dataclass
class Context:
    # noinspection GrazieInspection
    # because what's wrong with "Stores values", come on...
    """
    Stores values, which can be used in some commands and can vary each time the
    object of this class is created. Solves the circular dependencies problem.
    """

    vk_message_info: dict
    current_datetime: datetime.date


@dataclass
class ConstantContext:
    # noinspection GrazieInspection
    # because "dependencies" is the right word! I don't want to change it to
    # "dependencies'"!!!
    """
    Object of this class is created once and then used on commands that need
    constant metadata to work. Solves the circular dependencies problem.
    """

    commands: Tuple["CommandsSection", ...]
    command_descriptions: Dict[str, List[Callable[[], str]]]


class BaseMetadataElement(ABC):
    """
    Class for getting additional arguments to throw in the handler, which will
    help to handle a command.
    """

    @staticmethod
    @abstractmethod
    def get_data_from_context(context: Context) -> Any:
        """
        Returns any value, which can depend on the given context.

        Args:
            context: dict, where keys are str and values are whatever you want

        Returns:
            Any value
        """
        pass


class BaseConstantMetadataElement(ABC):
    """
    Class for getting constant additional arguments to throw in the handler,
    which will help to handle a command.
    """

    @staticmethod
    @abstractmethod
    def get_data_from_constant_context(
            constant_context: ConstantContext) -> Any:
        """
        Returns any value, which can depend on the given constant context.

        Args:
            constant_context:
                dict, where keys are str and values are whatever you want

        Returns:
            Any value
        """
        pass


class BaseConstantMetadata(ABC):

    @staticmethod
    @abstractmethod
    def get_data_from_context(context: ConstantContext) -> Any:
        pass


@dataclass
class ConvertedCommand:
    name: str
    arguments: list
