import gd


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


async def get_level_as_readable_string(level: gd.Level) -> str:
    description_str = (
        f"Описание: \"{level.description}\""
    ) if level.description else "Описание отсутствует"
    likes_amount_str = (
        f'Дизлайков: {-level.rating}'
    ) if level.rating < 0 else f'Лайков: {level.rating}'
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
    return (
        f"• Статистика для уровня \"{level.name}\":\n"
        f"\n"
        f"- Айди: {level.id}\n"
        f"- Автор: {level.creator.name}\n"
        f"- {description_str}\n"
        f"- Музыка: \"{level.song.name}\", айди - {level.song.id}\n"
        f"- Скачиваний: {level.downloads}\n"
        f"- {likes_amount_str}"  # Likes or dislikes
        f"{most_liked_comments_str}"
    )
