import subprocess
from datetime import datetime
from discord.ext.commands import Context

LOGFILE = 'log.txt'
STDOFILE = 'nohup.out'

def log(msg):
    with open(LOGFILE, 'a') as f:
        logged = f'[{datetime.now()}] {msg}\n'
        print(logged, end='')
        f.write(logged)

def logCommand(ctx, name, *args):
    argstr = f' with args: {list(args)}' if len(args) != 0 else ''
    log(f'Ran \'{name}\' on {ctx.channel.id} ({ctx.channel.guild.name}, #{ctx.channel.name}){argstr}')

def getlogs(n):
    if type(n) != int:
        return ''
    return subprocess.getoutput(f'tail --lines={n} {LOGFILE}')

def getstd(n):
    if type(n) != int:
        return ''
    return subprocess.getoutput(f'tail --lines={n} {STDOFILE}')
