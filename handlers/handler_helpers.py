import re
from dataclasses import dataclass
from typing import Generator

import bs4

from requests_workers.dataclasses_ import DemonInfo, Completion
from requests_workers.requests_worker import GET_POINTS_AMOUNT_REGEX
from vk.dataclasses_ import Message


@dataclass
class HandlingResult:

    text: str

    def to_message(self, peer_id: int) -> Message:
        return Message(self.text, peer_id)


def get_demons_info_from_bs4(
        soup: bs4.BeautifulSoup) -> Generator[DemonInfo, None, None]:
    # noinspection SpellCheckingInspection
    for raw_demon_info in soup.find_all(class_="vhaaFf qUO6Ue"):
        title, points, *completion_strings = raw_demon_info.stripped_strings
        divided_title = title.split("\"")
        demon_name = divided_title[1]
        if divided_title[2][1:6] == "(old)":
            authors_string = divided_title[2][10:]  # Removing " (old) by "
            is_old = True
        else:
            authors_string = divided_title[2][4:]  # Removing " by "
            is_old = False
        if authors_string.endswith("& more"):
            authors_string = authors_string[:-7]  # Removing " & more"
            there_is_more_authors = True
        else:
            there_is_more_authors = False
        authors_string = authors_string.replace("&", "и")
        pure_completions = []
        last_nickname = None
        # One completion info can look like
        # ["Nickname -", "https://you.rbutt/whTlVsmtR"]
        # or like
        # ["Nickname -", "https://you.rbutt/whTlVsmtR", "(666hz)"]
        # (They are not in the separate lists, [] just to be clear)
        for string in completion_strings:
            if string.startswith("(") and string.endswith("hz)"):
                pure_completions[-1].amount_of_hertz = int(string[1:-3])
            else:
                if last_nickname:  # Part we're parsing now is YT link
                    pure_completions.append(Completion(
                        nickname=last_nickname, video_link=string
                    ))
                    last_nickname = None
                else:  # Part we're parsing now is a nickname
                    last_nickname = string[:-2]  # Removing " -"
        points_amount = float(
            re.match(GET_POINTS_AMOUNT_REGEX, points).group(1)
        )
        yield DemonInfo(
            name=demon_name, is_old=is_old, authors=authors_string,
            there_is_more_authors=there_is_more_authors,
            points=points_amount, completed_by=pure_completions
        )
