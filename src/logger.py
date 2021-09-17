import subprocess
import util
from datetime import datetime
from discord.ext.commands import Bot
from shlex import quote

LOGFILE = 'log.txt'
LOGCHANNEL_ID = 888134572120891452
STDOFILE = 'nohup.out'
_logchannel = None

def setup(bot: Bot):
    global _logchannel
    _logchannel = bot.get_channel(LOGCHANNEL_ID)

async def logchannel(msg):
    await _logchannel.send(f'```{util.etb(msg)}```')

async def log(msg):
    with open(LOGFILE, 'a') as f:
        logged = f'[{datetime.now()}] {msg}\n'
        await logchannel(logged)
        print(logged, end='')
        f.write(logged)

async def logCommand(ctx, name, *args):
    argstr = f' with args: {list(args)}' if len(args) != 0 else ''
    await log(f'Ran \'{name}\' on {ctx.channel.id} ({ctx.channel.guild.name}, #{ctx.channel.name}){argstr}')

def getlogs(n):
    if type(n) != int:
        return 'No funny business.'
    return subprocess.getoutput(f'tail --lines={n} {quote(LOGFILE)}')

def getstd(n):
    if type(n) != int:
        return 'No funny business.'
    return subprocess.getoutput(f'tail --lines={n} {quote(STDOFILE)}')
