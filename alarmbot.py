from typing import Final
import os
from dotenv import load_dotenv
import lightbulb

# load discord token securely from server
load_dotenv()
TOKEN: Final[str] = os.getenv("DISCORD_TOKEN")

# initialize bot
bot: lightbulb.BotApp = lightbulb.BotApp(
    token=TOKEN,
    default_enabled_guilds=(1215341286173839402)
)
# load plugin functionalities from extensions folder
bot.load_extensions_from("./extensions")
# start bot
bot.run()
