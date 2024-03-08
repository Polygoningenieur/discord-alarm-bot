from typing import Final
import os
from dotenv import load_dotenv
import lightbulb
from datetime import datetime

# load discord token securely from server
load_dotenv()
TOKEN: Final[str] = os.getenv("DISCORD_TOKEN")

# set the alarm to none initially (this is global for the bot)
ALARM_TIME: datetime | None = None

# initialize bot
bot: lightbulb.BotApp = lightbulb.BotApp(
    token=TOKEN,
    default_enabled_guilds=(1215341286173839402)
)
# load plugin functionalities from extensions folder
bot.load_extensions_from("./extensions")
# start bot
bot.run()
