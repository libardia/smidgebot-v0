import discord, os, dotenv, datetime
from collections import defaultdict

dotenv.load_dotenv()
client = discord.Client()
logfile = 'log.txt'

# Logging ==================================

def log(msg):
    with open(logfile, 'a') as f:
        logged = f'[{datetime.datetime.now()}] {msg}\n'
        print(logged, end='')
        f.write(logged)

# Command decorator and storage ============

commands = {}

def command(func):
    async def wrapper(*args):
        log(f'Running command \'{func.__name__}\' with args {args[1:]}')
        await func(*args)
    commands[func.__name__] = wrapper
    return wrapper

# Commands =================================

@command
async def start(message):
    await message.channel.send(f'Okay, I\'ll remind everyone about the session!')

@command
async def test(message, a, b):
    await message.channel.send(f'{a} + {b} is {int(a) + int(b)}')

# Discord stuff ============================

@client.event
async def on_ready():
    log(f'We have logged in as "{client.user}"')

@client.event
async def on_message(message):
    if message.content.startswith('>>'):
        linetokens = message.content[2:].split(' ')
        command = linetokens[0].lower()
        args = tuple(linetokens[1:])
        try:
            await commands[command](message, *args)
        except KeyError:
            log(f'No command \'{command}\'')

client.run(os.getenv('TOKEN'))
