import traceback
import discord
from discord.ext import commands, tasks
from discord.ext.commands import command, Cog, Context, Bot

import util
import pickler
from logger import log, logCommand, getlogs, getstd, cleanLogs
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
        await logCommand(ctx, 'start')
        id = ctx.channel.id
        if id in self._invocations:
            await ctx.send('Don\'t worry, I\'m already keeping track.')
        else:
            inv = Invocation()
            # By default, 7pm CST on Saturday
            await inv.setRemtime((5, 19, 0))
            self._invocations[id] = inv
            stamp = util.tupleToNearestTimestamp(inv.remtime)
            await ctx.send(f'Ok, I\'ll remind everyone on <t:{stamp}:F>, which is <t:{stamp}:R>. I\'ll also send a reminder 30 minutes before that.')
            pickler.save(self._invocations)
    
    @command()
    async def stop(self, ctx: Context):
        '''
        Stop waiting for the correct time to send reminders.
        '''
        await logCommand(ctx, 'stop')
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
        await logCommand(ctx, 'exclude', name)
        id = ctx.channel.id
        if id in self._invocations:
            ex = self._invocations[id].exclude
            if name in ex:
                await ctx.send(util.discordEscape(f'{name} was already excluded.'))
            else:
                self._invocations[id].exclude.append(name)
                await ctx.send(util.discordEscape(f'Excluded {name}; I\'m now excluding {util.englishArray(ex, "no one")}.'))
                pickler.save(self._invocations)
        else:
            await ctx.send('I\'m not actually keeping track right now.')

    @command()
    async def include(self, ctx, name):
        '''
        Include a player from the reminder, if they have been previously excluded.
        '''
        await logCommand(ctx, 'include', name)
        id = ctx.channel.id
        if id in self._invocations:
            try:
                ex = self._invocations[id].exclude
                ex.remove(name)
                await ctx.send(util.discordEscape(f'Re-included {name}; I\'m now excluding {util.englishArray(ex, "no one")}.'))
                pickler.save(self._invocations)
            except ValueError:
                await ctx.send(util.discordEscape(f'{name} wasn\'t excluded in the first place.'))
        else:
            await ctx.send('I\'m not actually keeping track right now.')

    @command(name='reset-exclude')
    async def resetExclude(self, ctx):
        '''
        Clear the list of excluded players.
        '''
        await logCommand(ctx, 'reset-exclude')
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
        await logCommand(ctx, 'list-exclude')
        id = ctx.channel.id
        if id in self._invocations:
            await ctx.channel.send(util.discordEscape(f'Currently excluding {util.englishArray(self._invocations[id].exclude, "no one")}.'))
        else:
            await ctx.channel.send('I\'m not actually keeping track right now.')

    @command(name='change-time')
    async def changeTime(self, ctx, *timecode):
        '''
        Time must be in the format DDD HH:MM [AM/PM] ZZZ, where DDD is the three letter day of week and ZZZ is the three letter time zone.
        '''
        timecode = ' '.join(timecode)
        await logCommand(ctx, 'change-time', timecode)
        newtime = util.timecodeToTuple(timecode)
        id = ctx.channel.id
        if id in self._invocations:
            if newtime is not None:
                inv = self._invocations[id]
                await inv.setRemtime(newtime)
                stamp = util.tupleToNearestTimestamp(newtime)
                await ctx.send(f'Ok, the time I\'m waiting for has been changed to <t:{stamp}:F>, which is <t:{stamp}:R>.')
                pickler.save(self._invocations)
            else:
                await ctx.send(f'Sorry, I couldn\'t understand ``\u200d{util.etb(timecode)}\u200d`` as a time.')
        else:
            await ctx.channel.send('I\'m not actually keeping track right now.')
    
    @command()
    async def time(self, ctx):
        '''
        Show the currently set time when the reminder will be sent.
        '''
        await logCommand(ctx, 'time')
        id = ctx.channel.id
        if id in self._invocations:
            inv = self._invocations[id]
            stamp = util.tupleToNearestTimestamp(inv.remtime)
            await ctx.channel.send(f'Right now, I\'m set to remind everyone on <t:{stamp}:F>, which is <t:{stamp}:R>. I\'ll also send a reminder 30 minutes before that.')
        else:
            await ctx.channel.send('I\'m not actually keeping track right now.')

    @command()
    async def skip(self, ctx, number=None):
        '''
        Skip the next [number] sessions. If you don't give a number, tells you how many future sessions will be skipped. If instead of a number you write 'reset',
        the number of skipped sessions will be reset to 0.
        Also, when you call this multiple times, the skipped sessions add together; so '>>skip 2' followed by '>>skip 1' will result in the next
        three sessions being skipped.
        '''
        await logCommand(ctx, 'skip', number)
        id = ctx.channel.id
        inv = self._invocations[id]
        if id in self._invocations:
            if number is None:
                skip = inv.skipSessions
                await ctx.send(f'The next {skip} session{"" if skip == 1 else "s"} will be skipped.')
            elif number == 'reset':
                inv.skipSessions = 0
                pickler.save(self._invocations)
                await ctx.send('Ok, I won\'t skip any future sessions.')
            number = int(number)
            inv.skipSessions += number
            skip = inv.skipSessions
            pickler.save(self._invocations)
            await ctx.send(f'Ok, so in total, the next {skip} session{"" if skip == 1 else "s"} will be skipped.')

    async def doReminder(self, channel, remtype='current', istest=False):
        await log(f'Performing reminder of type "{remtype}"{" as a test" if istest else ""}...')
        id = channel.id
        if id in self._invocations:
            if self._invocations.skipSessions > 0:
                self._invocations.skipSessions -= 1
                pickler.save(self._invocations)
                return
            excluded = self._invocations[id].exclude
            at = '@\u200d' if istest else '@'
            reminder = f'Hey {at}everyone, '
            reminder += '30 minutes to D&D today!' if remtype == 'early' else 'D&D starting now!'
            if len(excluded) != 0:
                reminder += f'\nOh, and by the way, {util.discordEscape(util.englishArray(excluded))} can\'t make it.'
            await channel.send(reminder)
        else:
            await channel.send(f'Uh... no one told me to send reminders... I shouldn\'t be talking right now.')
    
    @command()
    async def test(self, ctx, remtype='current'):
        '''
        Test the reminder; this will omit the ping to 'everyone'. Also, add 'early' as an argument to test the 30-minutes-before reminder.
        '''
        await logCommand(ctx, 'test', remtype)
        await self.doReminder(ctx.channel, remtype, istest=True)

    @command()
    async def alive(self, ctx):
        '''
        The bot will reply that it's alive. Just to make sure it's running.
        '''
        await logCommand(ctx, 'alive')
        await ctx.send('Yes, hello, this is Smidge. The real Smidge, with all my squishy human insides. I am alive.')

    @command(hidden=True)
    async def dump(self, ctx):
        await logCommand(ctx, 'dump')
        await log('Dumping invocations dict')
        rep = 'invocations = {\n'
        first = True
        for id in self._invocations:
            inv = self._invocations[id]
            ch = self._bot.get_channel(id)
            if first:
                first = False
            else:
                rep += ',\n'
            rep += f'    \'{ch.guild.name}, #{ch.name}\': {{\n'
            rep += f'        \'exclude\': {inv.exclude},\n'
            rep += f'        \'remtime\': {inv.remtime},\n'
            rep += f'        \'remtimeEarly\': {inv.remtimeEarly},\n'
            rep += f'        \'mainCond\': {inv.mainCond},\n'
            rep += f'        \'earlyCond\': {inv.earlyCond},\n'
            rep += f'        \'skipSessions\': {inv.skipSessions}\n'
            rep +=  '    }'
        rep += '\n}'
        await ctx.send(f'```py\n{util.etb(rep)}```')
    
    @command(hidden=True)
    async def logs(self, ctx, lines=10):
        await logCommand(ctx, 'logs', lines)
        try:
            await ctx.send(f'```{util.etb(getlogs(int(lines)))}```')
        except:
            await ctx.send(f'Failed to get logs... sorry.\nException: ```{util.etb(traceback.format_exc())}```')
    
    @command(hidden=True)
    async def std(self, ctx, lines=10):
        await logCommand(ctx, 'std', lines)
        try:
            await ctx.send(f'```{util.etb(getstd(int(lines)))}```')
        except:
            await ctx.send(f'Failed to get stdout... sorry.\nException: ```{util.etb(traceback.format_exc())}```')

    @command(hidden=True, name='del-logs')
    async def delLogs(self, ctx: Context, arg=''):
        await logCommand(ctx, 'delete-logs', arg)
        all = True if arg == 'all' else False
        await ctx.send(f'Deleting {"ALL logs" if all else "all logs older than a week"}. Discord will rate limit this operation, so be aware this could take some time.')
        async with ctx.typing():
            n = await cleanLogs(all)
            await ctx.send(f'Deleted `{n}` logs.')

    @tasks.loop(seconds=0.5)
    async def _check(self):
        # await log('Check...')
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
        n = await cleanLogs()
        await log(f'Bot is alive. Deleted {n} old logs.')
    
def setup(bot):
    bot.add_cog(Reminders(bot))
