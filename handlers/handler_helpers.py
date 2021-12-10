import re
from dataclasses import dataclass
from typing import Generator, Union, List, Optional, Dict, Any

import bs4

from requests_workers import dataclasses_
from requests_workers.dataclasses_ import (
    DEMON_AUTHORS_OUTPUT_LIMIT, DEMON_RECORDS_OUTPUT_LIMIT
)
from requests_workers.requests_worker import RequestsWorker
from vk.dataclasses_ import Message

# noinspection SpellCheckingInspection
# because it uses machine-generated tag class names
CLASS_WITH_ONE_DEMON_NAME = "vhaaFf qUO6Ue"
# noinspection SpellCheckingInspection
COMPLETION_STRINGS_CLASS_NAME = (
    "hJDwNd-AhqUyc-uQSCkd jXK9ad D2fZ2 wHaque GNzUNc"
)
POINTS_REGEX = re.compile(r".+\(~(.+) ?points\)")
DEMON_NAME_REGEX = re.compile(
    r"\d+\.\s*"  # Demon number
    r"\"?(.+?)\"?\s+"  # Demon name
    r"((?:by|\(old\)).+?)\s*"  # Demon authors + whether the demon is old or not
    r"\(.+\)\s*"  # Points
)
AFTER_OLD_REGEX = re.compile(r"\(old\)\s*(.+)")
AFTER_BY_REGEX = re.compile(r"by\s*(.+)")
BEFORE_AND_MORE = re.compile(r"(.+?)\s*(?:and|&)\s*more")

AnyMobileDemonInfo = Union[
    dataclasses_.MobileDemonInfo, dataclasses_.CompactMobileDemonInfo
]


@dataclass
class HandlingResult:

    text: str

    def to_message(self, peer_id: int) -> Message:
        return Message(self.text, peer_id)


def get_mobile_demon_title_from_tag(tag: bs4.Tag):
    return tag.find(class_="tyJCtd mGzaTb baZpAe").text


def get_mobile_demon_info_from_tag(
        tag: bs4.Tag, demon_num: int,
        get_compact_demon_info: bool = False) -> AnyMobileDemonInfo:
    f"""
    Class with one demon is "{CLASS_WITH_ONE_DEMON_NAME}"
    """
    demon_title = get_mobile_demon_title_from_tag(tag)
    demon_name, after_name = DEMON_NAME_REGEX.fullmatch(demon_title).groups()
    match = AFTER_OLD_REGEX.fullmatch(after_name)
    if match:
        authors_string = match.group(1)
        is_old = True
    else:
        authors_string = AFTER_BY_REGEX.fullmatch(after_name).group(1)
        is_old = False
    match = BEFORE_AND_MORE.fullmatch(authors_string)
    if match:
        authors_string = match.group(1)
        there_is_more_authors = True
    else:
        there_is_more_authors = False
    authors_string = authors_string.replace("&", "и")
    if get_compact_demon_info:
        return dataclasses_.CompactMobileDemonInfo(
            place_in_list=demon_num,
            name=demon_name, is_old=is_old, authors=authors_string,
            there_is_more_authors=there_is_more_authors
        )
    pure_completions = []
    last_nickname = None
    completions_parsed = 0
    hertz_string_parts = []
    # noinspection SpellCheckingInspection
    for string in tag.find(
        class_=COMPLETION_STRINGS_CLASS_NAME
    ).stripped_strings:
        if string == "-":
            continue
        else:
            if string.startswith("("):
                hertz_string_parts.append(string)
            if hertz_string_parts:
                if not string.startswith("("):
                    hertz_string_parts.append(string)
                if string.endswith("hz)"):
                    pure_completions[-1].amount_of_hertz = int(
                        "".join(hertz_string_parts)[1:-3]
                    )
                    hertz_string_parts.clear()
            elif completions_parsed == DEMON_RECORDS_OUTPUT_LIMIT:
                break
            elif last_nickname:  # Part we're parsing now is YT link
                pure_completions.append(dataclasses_.Completion(
                    nickname=last_nickname, video_link=string
                ))
                last_nickname = None
                completions_parsed += 1
            else:  # Part we're parsing now is a nickname
                if string.endswith(" -"):
                    last_nickname = string[:-2]
                else:
                    last_nickname = string
    points_amount = float(
        POINTS_REGEX.fullmatch(demon_title).group(1)
    )
    return dataclasses_.MobileDemonInfo(
        place_in_list=demon_num,
        name=demon_name, is_old=is_old, authors=authors_string,
        there_is_more_authors=there_is_more_authors,
        points=points_amount, completed_by=pure_completions
    )


def get_mobile_demons_from_soup(
        soup: bs4.BeautifulSoup, limit: Optional[int] = None) -> List[bs4.Tag]:
    return soup.find_all(class_=CLASS_WITH_ONE_DEMON_NAME, limit=limit)


def get_mobile_demons_info_from_soup(
        soup: bs4.BeautifulSoup, limit: Optional[int] = None,
        get_compact_demon_info: bool = False
        ) -> Generator[AnyMobileDemonInfo, None, None]:
    return (
        get_mobile_demon_info_from_tag(
            raw_demon_info, demon_num=demon_num,
            get_compact_demon_info=get_compact_demon_info
        )
        for demon_num, raw_demon_info in enumerate(
            get_mobile_demons_from_soup(soup, limit=limit), start=1
        )
    )


def get_mobile_demon_info_from_soup_by_num(
        soup: bs4.BeautifulSoup, num: int) -> dataclasses_.MobileDemonInfo:
    return get_mobile_demon_info_from_tag(
        get_mobile_demons_from_soup(soup, limit=num)[num - 1], demon_num=num
    )


def get_compact_pc_demonlist_from_json(
        json_: List[dict]
        ) -> Generator[dataclasses_.CompactPCDemonInfo, None, None]:
    return (
        dataclasses_.CompactPCDemonInfo(
            place_in_list=demon_info["id"],
            name=demon_info["name"], publisher=demon_info["publisher"]["name"]
        )
        for demon_info in json_
    )


def get_pc_demon_from_json(json_: Dict[str, Any]) -> dataclasses_.PCDemonInfo:
    """
    json_ should be unpacked from "data" (response["data"])
    """
    first_ten_authors_names = [
        creator_info["name"]
        for creator_info in json_["creators"][:DEMON_AUTHORS_OUTPUT_LIMIT]
    ]
    first_five_records = [
        dataclasses_.DemonRecord(
            player_name=record_info["player"]["name"],
            percents=record_info["progress"],
            is_approved=record_info["status"] == "approved",
            video_link=record_info["video"]
        )
        for record_info in json_["records"][:DEMON_RECORDS_OUTPUT_LIMIT]
    ]
    return dataclasses_.PCDemonInfo(
        place_in_list=json_["id"],
        name=json_["name"], publisher=json_["publisher"]["name"],
        verifier=json_["verifier"]["name"],
        first_ten_authors_names=first_ten_authors_names,
        there_is_more_authors=(
            len(json_["creators"]) > DEMON_AUTHORS_OUTPUT_LIMIT
        ),
        first_five_records=first_five_records,
        there_is_more_records=(
            len(json_["records"]) > DEMON_RECORDS_OUTPUT_LIMIT
        ),
        video_link=json_["video"]
    )


def get_demon_name_from_stripped_strings(
        stripped_strings: Generator[bs4.NavigableString, None, None]) -> str:
    # split("\"", maxsplit=2)[1] here does this:
    # '1. "Title" by author' -> 'Title'
    return next(stripped_strings).split("\"", maxsplit=2)[1]


def get_demon_name_from_demon_tag(tag: bs4.Tag) -> str:
    return get_mobile_demon_title_from_tag(tag).split("\"", maxsplit=2)[1]


class HandlerHelpersWithDependencies:

    def __init__(self, requests_worker: RequestsWorker):
        self.requests_worker = requests_worker

    async def get_handling_result_about_pc_demon(self, demon_num: int):
        return HandlingResult(
            get_pc_demon_from_json(
                await self.requests_worker.get_pc_demon_as_json(demon_num)
            ).get_as_readable_string()
        )
