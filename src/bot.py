import os
import dotenv
import logger
from discord.ext import commands

dotenv.load_dotenv()
bot = commands.Bot(command_prefix='>>')
bot.load_extension('reminderscog')

@bot.event
async def on_ready():
    logger.setup(bot)
    await logger.log(f'BOT STARTED. We have logged in as "{bot.user}"')

bot.run(os.getenv('TOKEN'))
