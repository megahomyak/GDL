import configparser


# Unpacking vk_secrets.ini

_secret_config = configparser.ConfigParser()
_secret_config.read("vk/config/vk_secrets.ini", "utf-8")
# WARNING: vk_secrets.ini is not in the git, so you need to create it

TOKEN = _secret_config["SECRETS"]["token"]
GROUP_ID = int(_secret_config["SECRETS"]["group_id"])


# Unpacking vk_constants.ini

_constants_config = configparser.ConfigParser()
_constants_config.read("vk/config/vk_constants.ini", "utf-8")

SYMBOLS_PER_MESSAGE = int(_constants_config["MESSAGES"]["symbols_limit"])
DEBUG_CHAT_PEER_ID = int(_constants_config["ERRORS"]["debug_chat_peer_id"])
