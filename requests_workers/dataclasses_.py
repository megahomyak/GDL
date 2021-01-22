from dataclasses import dataclass
from typing import List


@dataclass
class Completion:
    nickname: str
    video_link: str
    amount_of_hertz: int = 60


@dataclass
class DemonInfo:
    name: str
    is_old: bool
    authors: str
    there_is_more_authors: bool
    points: float
    completed_by: List[Completion]
