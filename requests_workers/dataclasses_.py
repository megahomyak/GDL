from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Completion:
    nickname: str
    video_link: str
    amount_of_hertz: int = 60


@dataclass
class CompactMobileDemonInfo:
    place_in_list: int
    name: str
    is_old: bool
    authors: str
    there_is_more_authors: bool

    def get_as_readable_string(self) -> str:
        return (
            f"{self.place_in_list}. \"{self.name}\""
            f"{' (старый)' if self.is_old else ''} от {self.authors}"
            f"{' и других' if self.there_is_more_authors else ''}"
        )


@dataclass
class MobileDemonInfo(CompactMobileDemonInfo):
    points: float
    completed_by: List[Completion]

    def get_as_readable_string(self) -> str:
        who_completed_this_demon = []
        # noinspection PyUnboundLocalVariable
        # because demon_num will be at least 1 (see condition above)
        for completion_info in self.completed_by:
            if completion_info.amount_of_hertz == 60:
                hertz_amount_text = ""
            else:
                hertz_amount_text = f" ({completion_info.amount_of_hertz} герц)"
            who_completed_this_demon.append(
                f"{completion_info.nickname}{hertz_amount_text} "
                f"({completion_info.video_link})"
            )
        return (
            f"{self.place_in_list}. \"{self.name}\""
            f"{' (старый)' if self.is_old else ''} от "
            f"{self.authors}{' и других' if self.there_is_more_authors else ''}"
            f" (~{self.points} очков). А вот, кто этот уровень "
            f"прошел: {', '.join(who_completed_this_demon)}."
        )


@dataclass
class CompactPCDemonInfo:
    place_in_list: int
    name: str
    publisher: str

    def get_as_readable_string(self) -> str:
        return f"{self.place_in_list}. {self.name} от {self.publisher}"


@dataclass
class DemonRecord:
    player_name: str
    percents: int
    is_approved: bool
    video_link: str

    def get_as_readable_string(self) -> str:
        return (
            f"{self.player_name} - {self.percents}% ({self.video_link})"
            f"{'' if self.is_approved else ' [НЕ ПОДТВЕРЖДЕНО]'}"
        )


@dataclass
class PCDemonInfo(CompactPCDemonInfo):
    place_in_list: int
    verifier: str
    first_ten_authors_names: List[str]
    there_is_more_authors: bool
    first_five_records: List[DemonRecord]
    there_is_more_records: bool
    video_link: Optional[str]

    def get_as_readable_string(self) -> str:
        records_str = ',\n'.join(
            f"- {record.get_as_readable_string()}"
            for record in self.first_five_records
        ) if self.first_five_records else '<пусто>'
        records_ending = '\n и другие' if self.there_is_more_records else ''
        video_part = (
            f": {self.video_link}"
        ) if self.video_link is not None else " отсутствует"
        return (
            f"{self.name}:\n"
            f"Опубликован {self.publisher}, верифнут {self.verifier}.\n"
            f"Место в топе: {self.place_in_list}\n"
            f"\n"
            f"• Видео{video_part}\n"
            f"\n"
            f"• Авторы: {', '.join(self.first_ten_authors_names)}"
            f"{' и другие' if self.there_is_more_authors else ''}.\n"
            f"\n"
            f"• Рекорды:\n"
            f"{records_str}"
            f"{records_ending}."
        )
