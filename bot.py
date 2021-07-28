import os
import dotenv
from discord.ext import commands

dotenv.load_dotenv()
bot = commands.Bot(command_prefix='>>')
bot.load_extension('maincog')
bot.run(os.getenv('TOKEN'))
