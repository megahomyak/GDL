from dataclasses import dataclass
from typing import List


@dataclass
class Completion:
    nickname: str
    video_link: str
    amount_of_hertz: int = 60


@dataclass
class CompactDemonInfo:
    name: str
    is_old: bool
    authors: str
    there_is_more_authors: bool

    def get_as_readable_string(self) -> str:
        return (
            f"\"{self.name}\""
            f"{' (старый)' if self.is_old else ''} от {self.authors}"
            f"{' и других' if self.there_is_more_authors else ''}"
        )


@dataclass
class DemonInfo(CompactDemonInfo):
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
            f"\"{self.name}\"{' (старый)' if self.is_old else ''} от "
            f"{self.authors}{' и других' if self.there_is_more_authors else ''}"
            f" (~{self.points} очков). А вот, кто этот уровень "
            f"прошел: {', '.join(who_completed_this_demon)}."
        )
