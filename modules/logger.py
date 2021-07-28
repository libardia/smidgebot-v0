from datetime import datetime
from discord.ext.commands import Context

LOGFILE = 'log.txt'

def log(msg):
    with open(LOGFILE, 'a') as f:
        logged = f'[{datetime.now()}] {msg}\n'
        print(logged, end='')
        f.write(logged)

def logCommand(ctx, name, *args):
    log(f'Ran \'{name}\' on {ctx.channel.id} ({ctx.channel.guild.name}, #{ctx.channel.name}) with args: {list(args)}')
