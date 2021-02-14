from typing import Tuple


def get_plural(num: int, words: Tuple[str, str, str]) -> str:
    """
    Interesting features of russian language

    Argument `words` gonna be like
    ("слово", "слова", "слов") => 1 слово, 2 слова, 0 слов
    """
    if num == 1:
        return words[0]
    elif 2 <= num <= 4:
        return words[1]
    else:
        return words[2]
