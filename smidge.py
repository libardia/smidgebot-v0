import discord, os, dotenv, datetime, traceback
from discord.ext import tasks
from collections import defaultdict

dotenv.load_dotenv()
client = discord.Client()
logfile = 'log.txt'

# Logging / helpers ========================

def log(msg):
    with open(logfile, 'a') as f:
        logged = f'[{datetime.datetime.now()}] {msg}\n'
        print(logged, end='')
        f.write(logged)

def englishArray(list, empty='none'):
    if len(list) == 0:
        return empty
    elif len(list) == 1:
        return list[0]
    elif len(list) == 2:
        return f'{list[0]} and {list[1]}'
    else:
        string = ''
        for i, item in enumerate(list):
            if i != 0:
                string += ', '
            if i == len(list)-1:
                string += 'and '
            string += item
        return string

# Command decorator and storage ============

commands = {}

def command(func):
    async def wrapper(*args):
        log(f'Running command \'{func.__name__}\' with args {args[1:]}')
        await func(*args)
    commands[func.__name__] = wrapper
    return wrapper

# Storage ==================================

invocations = {}

# Commands =================================

@command
async def start(message):
    global invocations
    id = message.channel.id
    if id in invocations:
        await message.channel.send('Don\'t worry, I\'m already keeping track.')
    else:
        invocations[id] = {
            'message': message,
            'exclude': []
        }
        await message.channel.send('Ok, I\'ll remind everyone 30 minutes before and at the start of the session.')

@command
async def stop(message):
    global invocations
    id = message.channel.id
    if id in invocations:
        del invocations[id]
        await message.channel.send('Ok, I\'ll stop sending reminders.')
    else:
        await message.channel.send('I\'m not actually keeping track right now.')

@command
async def exclude(message, name):
    global invocations
    id = message.channel.id
    if id in invocations:
        ex = invocations[id]['exclude']
        if name in ex:
            await message.channel.send(f'{name} was already excluded.')
        else:
            invocations[id]['exclude'].append(name)
            await message.channel.send(f'Excluded {name}; I\'m now excluding {englishArray(ex, "no one")}.')
    else:
        await message.channel.send('I\'m not actually keeping track right now.')

@command
async def include(message, name):
    global invocations
    id = message.channel.id
    if id in invocations:
        try:
            ex = invocations[id]['exclude']
            ex.remove(name)
            await message.channel.send(f'Re-included {name}; I\'m now excluding {englishArray(ex, "no one")}.')
        except ValueError:
            await message.channel.send(f'{name} wasn\'t excluded in the first place.')
    else:
        await message.channel.send('I\'m not actually keeping track right now.')

@command
async def reset_exclude(message):
    global invocations
    id = message.channel.id
    if id in invocations:
        invocations[id]['exclude'] = []
        await message.channel.send('Excluded players reset.')
    else:
        await message.channel.send('I\'m not actually keeping track right now.')

@command
async def list_exclude(message):
    global invocations
    id = message.channel.id
    if id in invocations:
        await message.channel.send(f'Currently excluding {englishArray(invocations[id]["exclude"], "no one")}.')
    else:
        await message.channel.send('I\'m not actually keeping track right now.')

@command
async def help(message):
    data = {
        'help': 'Opens this menu.',
        'start': 'Start monitoring for the time to send reminders.',
        'stop': 'Stop monitoring to send reminders.',
        'exclude {name}': 'Exclude \'name\' from the reminder. In practice, this means the reminder will mention that they can\'t make it.',
        'include {name}': 'If someone was excluded, this undoes that.',
        'reset_exclude': 'Resets excluded users, so no one is excluded.',
        'list_exclude': 'Lists who is currently excluded.'
    }
    w = 15
    string = 'The prefix for all commands is `>>`.\n```'
    for cmd in data:
        string += f'{cmd:<{w}}    {data[cmd]}\n'
    string += '```'
    await message.channel.send(string)
    

# Discord stuff ============================

@client.event
async def on_ready():
    log(f'BOT STARTED. We have logged in as "{client.user}"')
    if not schedulerLoop.is_running():
        schedulerLoop.start()

@client.event
async def on_message(message):
    if message.content.startswith('>>') and message.author.id != client.user.id:
        linetokens = message.content[2:].split(' ')
        command = linetokens[0].lower()
        args = tuple(linetokens[1:])
        try:
            await commands[command](message, *args)
        except KeyError:
            log(f'No command \'{command}\'')
        except:
            log(traceback.format_exc())

lastCond1 = False
lastCond2 = False
@tasks.loop(seconds=1)
async def schedulerLoop():
    global lastCond1
    global lastCond2
    now = datetime.datetime.now()
    # cond1 = now.weekday() == 5 and now.hour == 18 and now.minute == 30 and now.second == 0
    # cond2 = now.weekday() == 5 and now.hour == 19 and now.minute == 00 and now.second == 0
    cond1 = now.weekday() == 0 and now.hour == 22 and now.minute == 30 and now.second == 0
    cond2 = now.weekday() == 0 and now.hour == 23 and now.minute == 00 and now.second == 0
    if cond1 and not lastCond1:
        for k in invocations:
            log('30 minute reminder')
            message = invocations[k]['message']
            excluded = invocations[k]['exclude']

            msg = 'Hey @everyone, 30 minutes to D&D today!'
            if len(excluded) != 0:
                msg += f'\nOh, and as a reminder, {englishArray(excluded)} can\'t make it today.'

            await message.channel.send(msg)
    if cond2 and not lastCond2:
        for k in invocations:
            log('current reminder')
            message = invocations[k]['message']
            excluded = invocations[k]['exclude']

            msg = 'Hey @everyone, D&D starting now!'
            if len(excluded) != 0:
                msg += f'\nOh, and as a reminder, {englishArray(excluded)} can\'t make it today.'

            await message.channel.send(msg)
    lastCond1 = cond1
    lastCond2 = cond2

client.run(os.getenv('TOKEN'))
