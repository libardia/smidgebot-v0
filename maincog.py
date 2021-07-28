import discord
from discord.ext import commands, tasks
from discord.ext.commands import command, Cog, Context, Bot

from modules.invocation import Invocation

class MainCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.invocations = {}
        self.LOGFILE = 'log.txt'  

    @Cog.listener()
    async def on_ready(self):
        pass

    @command()
    async def start(self, ctx: Context):
        id = ctx.channel.id
        if id in self.invocations:
            await ctx.send('Don\'t worry, I\'m already keeping track.')
        else:
            self.invocations[id] = Invocation(ctx)
            await ctx.send('Ok, I\'ll remind everyone 30 minutes before and at the start of the session.')

def setup(bot):
    bot.add_cog(MainCog(bot))