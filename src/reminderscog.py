import discord
from discord.ext import commands, tasks
from discord.ext.commands import command, Cog, Context, Bot

import util
import pickler
from logger import log, logCommand
from invocation import Invocation

class Reminders(Cog):
    def __init__(self, bot: Bot):
        self._bot = bot
        loaded = pickler.load()
        self._invocations = {} if loaded is None else loaded

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
            pickler.save(self._invocations)
    
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
            pickler.save(self._invocations)
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
                await ctx.send(f'{name} was already excluded.')
            else:
                self._invocations[id].exclude.append(name)
                await ctx.send(f'Excluded {name}; I\'m now excluding {util.englishArray(ex, "no one")}.')
                pickler.save(self._invocations)
        else:
            await ctx.send('I\'m not actually keeping track right now.')

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
                await ctx.send(f'Re-included {name}; I\'m now excluding {util.englishArray(ex, "no one")}.')
                pickler.save(self._invocations)
            except ValueError:
                await ctx.send(f'{name} wasn\'t excluded in the first place.')
        else:
            await ctx.send('I\'m not actually keeping track right now.')

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
            pickler.save(self._invocations)
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
                pickler.save(self._invocations)
            else:
                await ctx.send(f'Sorry, I couldn\'t understand `{timecode}` as a time.')
        else:
            await ctx.channel.send('I\'m not actually keeping track right now.')
    
    @command()
    async def time(self, ctx):
        '''
        Show the currently set time when the reminder will be sent.
        '''
        logCommand(ctx, 'time')
        id = ctx.channel.id
        if id in self._invocations:
            inv = self._invocations[id]
            await ctx.channel.send(f'Right now, I\'m set to remind everyone 30 minutes before and at the start of:\n{util.tupleToEnglish(inv.remtime)}')
        else:
            await ctx.channel.send('I\'m not actually keeping track right now.')

    async def doReminder(self, channel, remtype='current', istest=False):
        log(f'Performing reminder of type "{remtype}"{" as a test" if istest else ""}...')
        id = channel.id
        if id in self._invocations:
            excluded = self._invocations[id].exclude
            reminder = f'Hey {"[@]" if istest else "@"}everyone, '
            reminder += '30 minutes to D&D today!' if remtype == 'early' else 'D&D starting now!'
            if len(excluded) != 0:
                reminder += f'\nOh, and by the way, {util.englishArray(excluded)} can\'t make it.'
            await channel.send(reminder)
        else:
            await channel.send(f'Uh... no one told me to send reminders... I shouldn\'t be talking right now.')
    
    @command()
    async def test(self, ctx, remtype='current'):
        '''
        Test the reminder; this will omit the ping to 'everyone'. Also, add 'early' as an argument to test the 30-minutes-before reminder.
        '''
        logCommand(ctx, 'test', remtype)
        await self.doReminder(ctx.channel, remtype, istest=True)

    @command()
    async def alive(self, ctx):
        '''
        The bot will reply that it's alive. Just to make sure it's running.
        '''
        logCommand(ctx, 'alive')
        await ctx.send('Yes, hello, this is Smidge. The real Smidge, with all my squishy human insides. I am alive.')

    @command(hidden=True)
    async def dump(self, ctx):
        logCommand(ctx, 'dump')
        log(f'Dumping {self._invocations}')
        await ctx.send(f'```py\n{util.ppdict(self._invocations)}\n```')

    @tasks.loop(seconds=0.5)
    async def _check(self):
        # log('Check...')
        for id in self._invocations:
            ch = self._bot.get_channel(id)
            inv = self._invocations[id]
            earlyCond = util.testTime(inv.remtimeEarly)
            mainCond = util.testTime(inv.remtime)
            if earlyCond and not inv.earlyCond:
                await self.doReminder(ch, 'early')
            inv.earlyCond = earlyCond
            if mainCond and not inv.mainCond:
                await self.doReminder(ch)
            inv.mainCond = mainCond

    @tasks.loop(hours=1)
    async def _heartbeat(self):
        log('Bot is alive.')
        
def setup(bot):
    bot.add_cog(Reminders(bot))
