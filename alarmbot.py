import os
import lightbulb
from typing import Final
from dotenv import load_dotenv
from alarm.bot_context import BotContext

# load discord token securely from server
load_dotenv()
TOKEN: Final[str] = os.getenv("DISCORD_TOKEN")

# initialize bot
bot: lightbulb.BotApp = lightbulb.BotApp(
    token=TOKEN,
    default_enabled_guilds=(1215341286173839402)
)

# set bot to a global context so we can access him in the plugins as well
BotContext().set_bot(bot)

# load plugin functionalities from extensions folder
bot.load_extensions_from("./extensions")
# start bot
bot.run()
