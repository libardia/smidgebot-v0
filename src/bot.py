import os
import dotenv
from discord.ext import commands
from logger import log

dotenv.load_dotenv()
bot = commands.Bot(command_prefix='>>')
bot.load_extension('reminderscog')

@bot.event
async def on_ready():
    log(f'BOT STARTED. We have logged in as "{bot.user}"')

bot.run(os.getenv('TOKEN'))
