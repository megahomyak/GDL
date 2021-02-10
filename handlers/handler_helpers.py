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

AnyMobileDemonInfo = Union[
    dataclasses_.MobileDemonInfo, dataclasses_.CompactMobileDemonInfo
]


@dataclass
class HandlingResult:

    text: str

    def to_message(self, peer_id: int) -> Message:
        return Message(self.text, peer_id)


def get_mobile_demon_info_from_tag(
        tag: bs4.Tag, demon_num: int,
        get_compact_demon_info: bool = False) -> AnyMobileDemonInfo:
    f"""
    Class with one demon is "{CLASS_WITH_ONE_DEMON_NAME}"
    """
    title, points, *completion_strings = tag.stripped_strings
    divided_title = title.split("\"", maxsplit=2)
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
    if get_compact_demon_info:
        return dataclasses_.CompactMobileDemonInfo(
            place_in_list=demon_num,
            name=demon_name, is_old=is_old, authors=authors_string,
            there_is_more_authors=there_is_more_authors
        )
    pure_completions = []
    last_nickname = None
    completions_parsed = 0
    # One completion info can look like
    # ["Nickname -", "https://you.rbutt/whTlVsmtR"]
    # or like
    # ["Nickname -", "https://you.rbutt/whTlVsmtR", "(666hz)"]
    # (They are not in the separate lists, [] just to be clear)
    for string in completion_strings:
        if string.startswith("(") and string.endswith("hz)"):
            pure_completions[-1].amount_of_hertz = int(string[1:-3])
        else:
            if completions_parsed == DEMON_RECORDS_OUTPUT_LIMIT:
                break
            if last_nickname:  # Part we're parsing now is YT link
                pure_completions.append(dataclasses_.Completion(
                    nickname=last_nickname, video_link=string
                ))
                last_nickname = None
                completions_parsed += 1
            else:  # Part we're parsing now is a nickname
                last_nickname = string[:-2]  # Removing " -"
    points_amount = float(points[2:-8])  # Removing "(~" and " points)"
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
            place_in_list=demon_info["position"],
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
        place_in_list=json_["position"],
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


class HandlerHelpersWithDependencies:

    def __init__(self, requests_worker: RequestsWorker):
        self.requests_worker = requests_worker

    async def get_handling_result_about_pc_demon(self, demon_num: int):
        return HandlingResult(
            get_pc_demon_from_json(
                await self.requests_worker.get_pc_demon_as_json(demon_num)
            ).get_as_readable_string()
        )
