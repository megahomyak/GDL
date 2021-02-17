import gd

import utils

STARS_WORDS = ("звезда", "звезды", "звезд")


async def get_user_as_readable_string(user: gd.User) -> str:
    if user.role == gd.StatusLevel.MODERATOR:
        role = " [МОДЕРАТОР]"
    elif user.role == gd.StatusLevel.ELDER_MODERATOR:
        role = " [СТАРШИЙ МОДЕРАТОР]"
    else:
        role = ""
    creator_points_str = f"\n- Очков создания: {user.cp}\n" if user.cp else ""
    try:
        last_user_post_str = (
            f"\n- Последний пост игрока: "
            f"\"{(await user.get_page_comments())[0].body}\""
        )
    except (gd.NothingFound, IndexError):
        last_user_post_str = ""
    try:
        level_names_in_quotes = (
            f"\"{level.name}\""
            for level in (await user.get_levels_on_page())[0:3]
        )
    except gd.MissingAccess:
        last_user_levels_str = ""
    else:
        if level_names_in_quotes:
            last_user_levels_str = (
                f"\n- Последние 3 уровня игрока: "
                f"{', '.join(level_names_in_quotes)}"
            )
        else:
            last_user_levels_str = ""
    return (
        f"• Игрок {user.name}{role}:\n"
        f"\n"
        f"- Звезд на аккаунте: {user.stars}\n"
        f"- Алмазов на аккаунте: {user.diamonds}\n"
        f"- Монеток: {user.coins}\n"
        f"- Пользовательских монеток: {user.user_coins}\n"
        f"- Пройдено демонов: {user.demons}"
        f"{creator_points_str}"
        f"{last_user_post_str}"
        f"{last_user_levels_str}"
    )


async def get_level_as_readable_string(
        level: gd.Level, level_is_refreshed: bool = False) -> str:
    """
    level_is_refreshed means that `await level.refresh()` is used.
    You need to refresh a level to get its password (and other data, which isn't
    needed for this function)
    """
    description_str = (
        f"Описание: \"{level.description}\""
    ) if level.description else "Описание отсутствует"
    rating = level.rating
    likes_amount_str = (
        f'Дизлайков: {-rating}'
    ) if rating < 0 else f'Лайков: {rating}'
    top_three_comments = (
        await level.get_comments(gd.CommentStrategy.MOST_LIKED)
    )[0:3]
    if top_three_comments:
        top_three_comments_as_strings = []
        for position, comment in enumerate(top_three_comments, start=1):
            percentage_parenthesis = (
                f" ({comment.level_percentage}%)"
            ) if comment.level_percentage > 0 else ""
            top_three_comments_as_strings.append(
                f"{position}) \"{comment.body}\" от {comment.author.name}"
                f"{percentage_parenthesis}"
            )
        most_liked_comments_str = (
            "\n\nТоп 3 коммента:\n{}".format(
                '\n'.join(top_three_comments_as_strings)
            )  # Using format because Python don't like backslashes in f-strings
        )
    else:
        most_liked_comments_str = ""
    if not level_is_refreshed:
        # To get a password (and other data, which I don't need)
        await level.refresh()
    password_str = (
        f"- Пароль: {level.password}\n"
    ) if level.password else ""
    requested_stars = level.requested_stars
    requested_stars_word = utils.get_plural(requested_stars, STARS_WORDS)
    stars_amount = level.stars
    if stars_amount:
        if level.is_epic():
            featured_or_epic_str = " [Epic]"
        elif level.is_featured():
            featured_or_epic_str = " [Featured]"
        else:
            featured_or_epic_str = ""
        stars_word = utils.get_plural(stars_amount, STARS_WORDS)
        rate_str = (
            f"- Оценен на {stars_amount} {stars_word}{featured_or_epic_str}\n"
        )
    else:
        rate_str = ""
    return (
        f"• Статистика для уровня \"{level.name}\":\n"
        f"\n"
        f"- Айди: {level.id}\n"
        f"- Автор: {level.creator.name}\n"
        f"- {description_str}\n"
        # .title is more readable than .name
        f"- Сложность: {level.difficulty.title} "
        f"(запрошено {requested_stars} {requested_stars_word})\n"
        f"{password_str}"
        f"{rate_str}"
        f"- Музыка: \"{level.song.name}\", айди - {level.song.id}\n"
        f"- Скачиваний: {level.downloads}\n"
        f"- {likes_amount_str}"  # Likes or dislikes
        f"{most_liked_comments_str}"
    )
