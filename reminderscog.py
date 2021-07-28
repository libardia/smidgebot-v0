import discord
from discord.ext import commands, tasks
from discord.ext.commands import command, Cog, Context, Bot

from modules import util
from modules.logger import log, logCommand
from modules.invocation import Invocation

class Reminders(Cog):
    def __init__(self, bot: Bot):
        self._bot = bot
        self._invocations = {}

    @Cog.listener()
    async def on_ready(self):
        # This is here because pylint can't tell that start() exists on these, for some reason.
        # pylint: disable=no-member
        self._heartbeat.start()
        self._check.start()

    @command()
    async def start(self, ctx: Context):
        '''
        Start waiting for the correct time to send reminders.
        '''
        logCommand(ctx, 'start')
        id = ctx.channel.id
        if id in self._invocations:
            await ctx.send('Don\'t worry, I\'m already keeping track.')
        else:
            inv = Invocation(ctx, log)
            self._invocations[id] = inv
            await ctx.send(f'Ok, I\'ll remind everyone 30 minutes before and at the start of:\n{util.tupleToEnglish(inv.remtime)}')
    
    @command()
    async def stop(self, ctx: Context):
        '''
        Stop waiting for the correct time to send reminders.
        '''
        logCommand(ctx, 'stop')
        id = ctx.channel.id
        if id in self._invocations:
            self._invocations.pop(id)
            await ctx.send('Ok, I\'ll stop sending reminders.')
        else:
            await ctx.send('I\'m not actually keeping track right now.')
    
    @command()
    async def exclude(self, ctx, name):
        '''
        Exclude a player from the reminder; in practice, this means that the reminder will mention that they can't make it.
        '''
        logCommand(ctx, 'exclude', name)
        id = ctx.channel.id
        if id in self._invocations:
            ex = self._invocations[id].exclude
            if name in ex:
                await ctx.channel.send(f'{name} was already excluded.')
            else:
                self._invocations[id].exclude.append(name)
                await ctx.channel.send(f'Excluded {name}; I\'m now excluding {util.englishArray(ex, "no one")}.')
        else:
            await ctx.channel.send('I\'m not actually keeping track right now.')

    @command()
    async def include(self, ctx, name):
        '''
        Include a player from the reminder, if they have been previously excluded.
        '''
        logCommand(ctx, 'include', name)
        id = ctx.channel.id
        if id in self._invocations:
            try:
                ex = self._invocations[id].exclude
                ex.remove(name)
                await ctx.channel.send(f'Re-included {name}; I\'m now excluding {util.englishArray(ex, "no one")}.')
            except ValueError:
                await ctx.channel.send(f'{name} wasn\'t excluded in the first place.')
        else:
            await ctx.channel.send('I\'m not actually keeping track right now.')

    @command(name='reset-exclude')
    async def resetExclude(self, ctx):
        '''
        Clear the list of excluded players.
        '''
        logCommand(ctx, 'reset-exclude')
        id = ctx.channel.id
        if id in self._invocations:
            self._invocations[id].exclude = []
            await ctx.channel.send('Excluded players reset.')
        else:
            await ctx.channel.send('I\'m not actually keeping track right now.')

    @command(name='list-exclude')
    async def listExclude(self, ctx):
        '''
        Show the list of excluded players.
        '''
        logCommand(ctx, 'list-exclude')
        id = ctx.channel.id
        if id in self._invocations:
            await ctx.channel.send(f'Currently excluding {util.englishArray(self._invocations[id].exclude, "no one")}.')
        else:
            await ctx.channel.send('I\'m not actually keeping track right now.')

    @command(name='change-time')
    async def changeTime(self, ctx, *timecode):
        '''
        Time must be in the format DDD HH:MM [AM/PM] ZZZ, where DDD is the three letter day of week and ZZZ is the three letter time zone.
        '''
        timecode = ' '.join(timecode)
        logCommand(ctx, 'change-time', timecode)
        newtime = util.timecodeToTuple(timecode)
        id = ctx.channel.id
        if id in self._invocations:
            if newtime is not None:
                inv = self._invocations[id]
                inv.setRemtime(newtime)
                await ctx.send(f'Ok, the time I\'m waiting for has been changed to:\n{util.tupleToEnglish(inv.remtime)}')
            else:
                await ctx.send(f'Sorry, I couldn\'t understand `{timecode}` as a time.')
        else:
            await ctx.channel.send('I\'m not actually keeping track right now.')

    
    @command(name='test')
    async def doReminder(self, ctx, remtype='current'):
        '''
        Test the reminder; this will ping 'everyone', so be careful. Also, add 'early' as an argument to test the 30-minutes-before reminder.
        '''
        logCommand(ctx, 'doReminder', remtype)
        id = ctx.channel.id
        if id in self._invocations:
            excluded = self._invocations[id].exclude
            reminder = 'Hey @everyone, '
            reminder += '30 minutes to D&D today!' if remtype == 'early' else 'D&D starting now!'
            if len(excluded) != 0:
                reminder += f'\nOh, and by the way, {util.englishArray(excluded)} can\'t make it.'
            await ctx.send(reminder)
        else:
            await ctx.send(f'Uh... no one told me to send reminders... I shouldn\'t be talking right now.')
    
    @command()
    async def alive(self, ctx):
        '''
        The bot will reply that it's alive. Just to make sure it's running.
        '''
        logCommand(ctx, 'alive')
        await ctx.send('Yes, hello, this is Smidge. The real Smidge, with all my squishy human insides. I am alive.')

    @tasks.loop(seconds=0.5)
    async def _check(self):
        # log('Check...')
        for id in self._invocations:
            inv = self._invocations[id]
            earlyCond = util.testTime(inv.remtimeEarly)
            mainCond = util.testTime(inv.remtime)
            if earlyCond and not inv.earlyCond:
                await self.doReminder(inv.ctx, 'early')
            inv.earlyCond = earlyCond
            if mainCond and not inv.mainCond:
                await self.doReminder(inv.ctx)
            inv.mainCond = mainCond

    @tasks.loop(hours=1)
    async def _heartbeat(self):
        log('Bot is alive.')
        
def setup(bot):
    bot.add_cog(Reminders(bot))